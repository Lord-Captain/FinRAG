# 该脚本用于：文本预处理

import jieba
import os, sys
# 1. 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 2. 获取当前目录的上级目录
module_dir = os.path.dirname(current_dir)

# 3. 获取项目根目录的绝对路径
project_root = os.path.dirname(module_dir)

# 4. 将项目根目录加入系统路径, 确保跨目录导入自定义模块(例如：config, logger)
sys.path.insert(0, project_root)

from base import logger

# todo 1. 定义文本预处理函数
def preprocess_text(text):
    # 预处理文本
    logger.info('开始预处理文本')
    try:
        # 分词并转换为小写
        return jieba.lcut(text.lower())
    except AttributeError as e:
        # 记录预处理失败
        logger.error(f'文本预处理失败:{e}')
        # 返回空列表
        return []

if __name__ == '__main__':
    # 1. 调用preprocess_text()函数, 测试
    print(preprocess_text('这是一个测试文本'))