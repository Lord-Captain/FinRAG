# 该脚本用于BM25搜索，阈值>= 0.85才会走MySQL系统

from rank_bm25 import BM25Okapi     # 导入BM25算法
import numpy as np
import os, sys
# 1. 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. 获取当前目录的上级目录
module_dir = os.path.dirname(current_dir)

# 3. 获取项目根目录的绝对路径
project_root = os.path.dirname(module_dir)

# 4. 将项目根目录加入系统路径, 确保跨目录导入自定义模块(例如：config, logger)
sys.path.insert(0, project_root)

from mysql_qa.db.mysql_client import MySQLClient
from mysql_qa.cache.redis_client import RedisClient
from mysql_qa.utils.preprocess import preprocess_text
from base import logger

# todo 1. 定义BM25搜素类 -> 封装数据加载, 模型初始化, 相似度计算, 答案检索等...
class BM25Search():
    # todo 1.1 初始化函数 -> 客户端实例, 模型参数, 加载数据
    def __init__(self, redis_client, mysql_client):
        # 1. 日志实例
        self.logger = logger
        # 2. Redis客户端实例
        self.redis_client = redis_client
        # 3. MySQL客户端实例
        self.mysql_client = mysql_client
        # 4. 初始化BM25模型
        self.bm25 = None
        # 5. 初始化分词后的问题列表
        self.questions = None
        # 6. 初始化原始问题列表
        self.original_questions = None
        # 7. 调用数据加载方法 -> 加载问题数据并, 初始化模型
        self._load_data()

    # todo 1.2 数据加载方法 -> 优先从Redis缓存加载, 缓存未命中则从MySQL加载
    def _load_data(self):
        # 1. 定义Redis缓存键 -> 区分原始问题和分词后问题的缓存
        original_key = 'qa_original_questions'      # 原始问题缓存键
        tokenized_key = 'qa_tokenized_questions'    # 分词后问题缓存键

        # 2. 从Redis中获取原始问题 -> 缓存读取速度快, 减少数据库访问
        self.original_questions = self.redis_client.get_data(original_key)
        # print(f'original_questions: {self.original_questions}')

        # 3. 从Redis中获取分词后的问题
        tokenized_questions = self.redis_client.get_data(tokenized_key)
        # print(f'tokenized_questions: {tokenized_questions}')


        # 4. 若Redis缓存中无数据(或数据不完整) -> 则从MySQL加载并更新缓存
        if not self.original_questions or not tokenized_questions:                  # 这里是and会不会好一些？
            # 4.1 从MySQL获取原始文件列表, 格式为 元组嵌套, 例如:((问题1,),(问题2,)...)
            self.original_questions = self.mysql_client.fetch_questions()
            # print(f'original_questions: {self.original_questions}')

            # 4.2 若MySQL也无问题数据, 记录警告日志并返回
            if not self.original_questions:
                self.logger.warning('未从MySQL加载到任何问题数据')
                return None

            # 4.3 对原始问题进行分词处理 -> 转换为词语列表
            # 注意: q[0]是因为原始问题的格式是元组嵌套: (('问题1',),('问题2',),...))
            tokenized_questions = [preprocess_text(q[0]) for q in self.original_questions]

            # 4.4 将原始问题列表转换为字符串 -> 去除元组嵌套, 并存储到Redis中
            self.redis_client.set_data(original_key, [(q[0]) for q in self.original_questions])
            self.redis_client.set_data(tokenized_key, tokenized_questions)

        # 5. 保存分词后的问题列表 -> 用于BM25模型初始化
        self.questions = tokenized_questions
        # print(f'用于BM25模型初始化:{self.questions}')

        # 6. 初始化BM25模型
        self.bm25 = BM25Okapi(self.questions)

        # 7. 记录info日志
        self.logger.info('BM25模型初始化成功')

    # todo 1.3 softmax分数归一化方法 -> 将BM25分数转换为概率分布, 便于阈值判断
    def _softmax(self, scores):
        # 对输入的分数进行softmax归一化, 输出总和为1的概率分布
        # 1. 计算指数分数
        exp_scores = np.exp(scores - np.max(scores))
        # 2. 返回归一化结果
        return exp_scores / np.sum(exp_scores)
    # todo 1.4 核心搜索方法: 处理查询, 计算相似度, 返回匹配答案 或 提示无结果
    def search(self, query, threshold = 0.85):
        """

        :param query:
        :param threshold:
        :return: 匹配成功(答案, False); 匹配失败(None, True); False表示非新查询，即命中缓存
        """
        # 1. 检查查询有效性 -> 空或非字符串类型认为无效
        if not query or not isinstance(query, str):
            self.logger.error('无效查询: 查询为空或者非空字符串类型')
            return None, True

        # 2. 走这里(肯定是非空字符串), 先检查Redis缓存 -> 缓存命中则直接返回
        cached_answer = self.redis_client.get_answer(query)
        if cached_answer:
            self.logger.info(f'从Redis缓存中获取答案成功:{query}')
            return cached_answer, False

        # 3. 走到这里，说明缓存未命中, 需要从数据库中查询
        try:
            # 3.1 对查询文本进行预处理 -> 分词, 和问题库预处理逻辑一致
            print(f'当前query:{query}')
            query_tokens = preprocess_text(query)
            # 3.2 计算查询与所有问题的BM25相似度
            scores = self.bm25.get_scores(query_tokens)
            # 3.3 对分数进行归一化处理 -> 转换为概率分布
            softmax_score = self._softmax(scores)
            # 3.4 找到最高相似度对应的索引和分数
            best_idx = softmax_score.argmax()
            best_score = softmax_score[best_idx]
            print(f'best_idx:{best_idx}, best_score:{best_score}')

            # 4. 若最高分超过阈值，视为匹配成功
            if best_score >= threshold:

                original_question = self.original_questions[best_idx]
                # print(f'original_question:{original_question}')

                answer = self.mysql_client.fetch_answer(original_question)
                # print(f'answer:{answer}')
                if answer:
                    # 7.3 将 查询-答案 缓存到Redis中 -> 供下次查询使用
                    self.redis_client.set_data(f'answer:{query}', answer)
                    # 记录INFO级日志：搜索成功及相似度
                    self.logger.info(f'搜索成功，相似度;{best_score: .3f}')
                    return answer, False

            # 若未超过阈值，记录INFO级日志并返回结果
            self.logger.info(f'未找到答案，最高匹配度:{best_score:.3f}(低于阈值{threshold:.3f})')
            return None, True


        except Exception as e:
            self.logger.error(f'数据库查询异常:{e}')
            return None, True


if __name__ == '__main__':
    # 1. 实例化Redis和MySQL客户端
    redis_client = RedisClient()
    mysql_client = MySQLClient()

    # 2. 创建BM25搜素实例
    bm25_search = BM25Search(redis_client, mysql_client)

    # 3. 测试搜索功能, 例如: 查询'安装VMware时显示灰色如何解决'
    result = bm25_search.search(query='安装VMware时显示灰色如何解决')
    print(f'result:\n {result}')
