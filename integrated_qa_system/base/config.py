# 该文件用于：管理配置文件（FinRAG - 金融智能问答系统）

import configparser             # 导入配置文件解析库，解析INI格式的配置文件
import os                       # 导入路径操作模块
import json                     # 导入json解析模块


# todo 1. 配置文件路径计算
# 1. 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# print(f'current_file_path:{current_file_path}') # D:\Python\pythonProject\FinRAG\integrated_qa_system\base\config.py

# 2. 获取当前文件所在目录的绝对路径
current_dir_path = os.path.dirname(current_file_path)
# print(f'current_dir_path:{current_dir_path}')   # D:\Python\pythonProject\FinRAG\integrated_qa_system\base

# 3. 获取当前文件根目录的绝对路径
project_root = os.path.dirname(current_dir_path)    # D:\Python\pythonProject\FinRAG\integrated_qa_system
# print(f'project_root:{project_root}')

# 4. 拼接配置文件(config.ini)
config_file_path = os.path.join(project_root, 'config.ini')
# print(f'config_file_path:{config_file_path}')

# todo 2. 配置解析类 -> 封装配置文件读取逻辑，提供统一的配置参数访问接口
class Config():
    # todo 2.1 构造函数，初始化方法，读取配置文件并解析各服务的配置参数
    def __init__(self, config_file = config_file_path):
        # 1. 创建配置文件解析器实例
        self.config = configparser.ConfigParser()
        # 2. 读取配置文件 -> 根据传入的路径加载ini文件内容
        self.config.read(config_file, encoding='utf-8')

        self.PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
        self.DATA_DIR = os.path.join(self.PROJECT_ROOT, 'rag_qa/data')
        self.EDU_DOCUMENT_LOADERS_DIR = os.path.join(self.PROJECT_ROOT, 'rag_qa/edu_document_loaders')

        # 3. 解析并存储各服务配置参数
        # 3.1 解析MySQL数据库配置
        self.MYSQL_HOST = self.config.get('mysql', 'host', fallback='localhost')
        self.MYSQL_USER = self.config.get('mysql', 'user', fallback='root')
        self.MYSQL_PASSWORD = self.config.get('mysql', 'password', fallback='123456')
        self.MYSQL_DATABASE = self.config.get('mysql', 'database', fallback='subjects_kg')

        # 3.2 解析Redis数据库配置
        self.REDIS_HOST = self.config.get('redis', 'host', fallback='localhost')
        self.REDIS_PORT = self.config.get('redis', 'port', fallback='6379')
        self.REDIS_PASSWORD = self.config.get('redis', 'password', fallback='1234')
        self.REDIS_DB = self.config.get('redis', 'db', fallback=0)

        # 3.3 解析日志配置
        # 日志文件路径：从[logger]节点的log_file键获取，默认值为: logs/app.log
        self.LOG_FILE = self.config.get('logger', 'log_file', fallback='logs/app.log')

        # 3.4 解析Milvus配置
        self.MILVUS_HOST = self.config.get('milvus', 'host', fallback='localhost')
        self.MILVUS_PORT = self.config.get('milvus', 'port', fallback='19530')
        self.MILVUS_DATABASE_NAME = self.config.get('milvus', 'database_name', fallback='itcast')
        self.MILVUS_COLLECTION_NAME = self.config.get('milvus', 'collection_name', fallback='edurag_final')

        # 3.5 解析LLM
        self.LLM_MODEL = self.config.get('llm', 'model', fallback='qwen-plus')
        self.DASHSCOPE_API_KEY = self.config.get('llm', 'dashscope_api_key', fallback='') # fallback写上你自己的api-key
        self.DASHSCOPE_BASE_URL = self.config.get('llm', 'dashscope_base_url', fallback='https://dashscope.aliyuncs.com/compatible-mode/v1')

        # 3.6 检索参数配置
        self.PARENT_CHUNK_SIZE = int(self.config.get('retrieval','parent_chunk_size', fallback=1200))
        self.CHILD_CHUNK_SIZE = int(self.config.get('retrieval','child_chunk_size', fallback=300))
        self.CHUNK_OVERLAP = int(self.config.get('retrieval','chunk_overlap', fallback=50))
        self.RETRIEVAL_K = int(self.config.get('retrieval','retrieval_k', fallback=3))
        self.CANDIDATE_M = int(self.config.get('retrieval','candidate_m', fallback=2))

        # 3.7 应用配置
        # 解析领域列表为真正的Python列表(而非字符串)
        raw_sources = self.config.get('app', 'valid_sources', fallback='["stock","fund","bank","insurance","futures"]')
        self.VALID_SOURCES = json.loads(raw_sources)
        # 领域代码 -> 中文名称映射
        self.SOURCE_NAMES = {
            'stock': '股票',
            'fund': '基金',
            'bank': '银行',
            'insurance': '保险',
            'futures': '期货'
        }
        self.CUSTOMER_SERVICE_PHONE = self.config.get('app','customer_service_phone',fallback='12345678')


# todo 3. 创建全局配置实例 -> 供其他模块直接导入使用
config = Config()


if __name__ == '__main__':
    # 1. 手动配置文件路径 -> 用于测试，实际使用可忽略
    # config_file = r'D:\Python\pythonProject\FinRAG\integrated_qa_system\config.ini'
    config_file = r'..\config.ini'

    # 2. 实例化Config类 -> 加载并解析配置文件
    conf = Config(config_file)

    # 3. 打印测试
    print(f'mysql:{conf.MYSQL_DATABASE}')
    print(f'redis:{conf.REDIS_DB}')
    print(f'log:{conf.LOG_FILE}')
    print(f'PARENT_CHUNK_SIZE:{conf.PARENT_CHUNK_SIZE},type:{type(conf.PARENT_CHUNK_SIZE)}')
