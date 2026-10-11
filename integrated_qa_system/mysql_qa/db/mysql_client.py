# 该脚本用于：MySQL数据库的基础操作

import pymysql
import pandas as pd
import sys, os

# todo 1. 路径配置
# 1. 获取当前文件所在目录的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
# print(f'current_dir:{current_dir}')   # D:\Python\pythonProject\EduRAG\integrated_qa_system\mysql_qa\db

# 2. 获取当前文件根目录的绝对路径
module_dir = os.path.dirname(current_dir)    # D:\Python\pythonProject\EduRAG\integrated_qa_system\mysql_qa
# print(f'project_root:{project_root}')

# 3. 获取当前文件根目录的绝对路径
project_root = os.path.dirname(module_dir)    # D:\Python\pythonProject\EduRAG\integrated_qa_system
# print(f'project_root:{project_root}')

# 4. 将项目根目录插入系统路径
sys.path.insert(0, project_root)

# 5. 导入自定义模块
from base import Config, logger

# todo 2. 定义MySQL客户端类 -> 封装数据库连接，取操作数据增查、连接关闭等功能
class MySQLClient():
    # todo 2.1 初始化方法 -> 建立数据库，创建游标，处理连接异常
    def __init__(self):
        self.logger = logger
        try:
            # 2. 建立MySQL数据库连接 -> 从config中读取编码
            self.connection = pymysql.connect(
                host = Config().MYSQL_HOST,
                user = Config().MYSQL_USER,
                password = Config().MYSQL_PASSWORD,
                database = Config().MYSQL_DATABASE
            )
            # 3. 创建游标对象 -> 用于执行SQL语句并返回结果
            self.cursor = self.connection.cursor()

            # 4. 记录info日志
            self.logger.info('MySQL 连接成功')
        except pymysql.MySQLError as e:
            # 5. 记录error日志 -> 输出错误信息
            self.logger.error(f'MySQL 连接失败:{e}')
            raise   # 抛出异常不屏蔽错误，让调用方感知连接失败

    # todo 2.1 初始化方法 -> 建立数据库，创建游标，处理连接异常
    def create_table(self):
        # 1. 定义创建表的SQL语句
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS jpkb(
            id INT AUTO_INCREMENT PRIMARY KEY,      # 自增主键
            subject_name VARCHAR(20),               # 领域名称
            question VARCHAR(1000),                 # 问题内容
            answer VARCHAR(1000)                    # 答案内容
            )
        '''
        try:
            # 2. 执行SQL语句 -> 创建表
            self.cursor.execute(create_table_query)
            # 3. 提交事务 ->  确认表创建成功. MySQL默认事务需要手动提交，确保表创建成功
            self.connection.commit()
            # 4. 记录日志
            self.logger.info('表创建成功')
        except pymysql.MySQLError as e:
            # 5. 输出错误信息
            self.logger.error(f'创建表失败: {e}')
            # 抛出异常，不屏蔽错误，让调用方感知数据插入失败
            raise

    # todo 2.3 从csv文件批量插入数据到 jpkb表中
    def insert_data(self, csv_path):
        try:
            # 1. 读取csv文件 -> 获取数据
            data = pd.read_csv(csv_path)
            # 扩展: 打印下，查看数据
            # print(data.head())
            # 2. 循环遍历csv每一行数据 -> 执行插入操作。
            for _, row in data.iterrows():
                # 2.1 构建插入数据的SQL语句, 使用%s占位符, 避免SQL注入攻击问题
                insert_query = """
                INSERT INTO jpkb (subject_name, question, answer)
                VALUES (%s, %s, %s)
                """
                # 2.2 执行SQL语句 -> 插入数据，将csv行数据(领域类别, 问题, 答案)传入占位符
                self.cursor.execute(insert_query, (row['类别'], row['问题'], row['答案']))

                # 3. 提交事务 -> 确认数据插入成功
                self.connection.commit()
                # 4. 输出信息日志 -> 确认数据插入成功
                self.logger.info('MySQL数据插入成功')


        except Exception as e:
            # 5. 捕获异常信息，回滚事务，抛出异常
            # 5.1 输出错误信息
            self.logger.error(f'数据插入失败:{e}')
            # 5.2 事务回滚: 把数据库连接恢复到事务开始前的状态 -> 类似于: Linux的快照
            self.connection.rollback()
            # 5.3 抛出异常，不屏蔽错误，让调用方感知数据插入失败
            raise

    # todo 2.4 从jpkb表中获取所有问题(返回问题列表)
    def fetch_questions(self):
        try:
            # 1. 执行SQL查询
            self.cursor.execute("select question from jpkb")
            # 2. 获取查询结果。fetch_all(): 返回所有匹配数据
            results = self.cursor.fetchall()
            # 3. 记录INFO日志->确认数据查询成功
            self.logger.info('MySQL数据查询成功')
            # 4. 返回查询结果
            return results

        except pymysql.MySQLError as e:
            # 5.输出错误信息
            self.logger.error(f'数据查询失败:{e}')
            # 返回空列表, 避免异常
            return []

    # todo 2.5 根据指定问题从jpkb表中获取对应答案
    def fetch_answer(self, question):
        # 1. 执行SQL查询
        try:
            self.cursor.execute("select answer from jpkb where question = %s", (question,)) # 占位符方式, 避免SQL注入攻击
            # 2. 获取查询结果
            result = self.cursor.fetchone() # 获取单行数据
            # 3. 输出查询到的结果
            # print(f'result:{result}')
            # 4. 处理结果: 有匹配数据则返回答案(取元组的第1个元素), 无匹配则返回None
            return result[0]
        except pymysql.MySQLError as e:
            self.logger.error(f'答案获取失败:{e}')
            return None

    # todo 2.6 关闭MySQL连接，释放资源，避免内存泄漏
    def close(self):    # 拓展，什么是数据库连接池？
        # 关闭数据库连接
        try:
            # 关闭连接
            self.connection.close()
            # 记录关闭成功
            self.logger.info('MySQL 连接已关闭')

        except pymysql.MySQLError as e:
            # 记录关闭失败
            self.logger.error(f'关闭连接失败:{e}')


if __name__ == '__main__':
    # 连接数据库
    mysql_client = MySQLClient()
    # 创建数据表
    # mysql_client.create_table()
    # 插入数据
    # mysql_client.insert_data(csv_path='../data/JP学科知识问答.csv')
    questions = mysql_client.fetch_questions()
    print(questions)

    answer = mysql_client.fetch_answer('关联子查询的执行顺序是什么')
    print(answer)

    # 关闭数据库连接
    mysql_client.close()