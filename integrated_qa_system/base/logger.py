# 该脚本用于：设置日志

import logging
import os
from config import Config
# todo 1. 记录日志文件的最终保存路径
# 1. 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
# print(f'current_file_path:{current_file_path}') # D:\Python\pythonProject\EduRAG\integrated_qa_system\base\logger.py

# 2. 获取当前文件所在目录的绝对路径
current_dir_path = os.path.dirname(current_file_path)
# print(f'current_dir_path:{current_dir_path}')   # D:\Python\pythonProject\EduRAG\integrated_qa_system\base

# 3. 获取当前文件根目录的绝对路径
project_root = os.path.dirname(current_dir_path)    # D:\Python\pythonProject\EduRAG\integrated_qa_system
# print(f'project_root:{project_root}')

# 4. 拼接配置文件(logs\app.log)
log_file = os.path.join(project_root, Config().LOG_FILE)
# print(f'config_file_path:{log_file}')

# todo 2. 封装日志配置函数 -> 可重复使用的双输出日志
def setup_logger(log_file = log_file):
    """
    :param log_file:
    :return:
    """
    # 1. 确保日志文件存在
    # 参1: 获取日志文件的所在目录   参2: 如果目录已存在，不报错; 如果不存在, 处理器筛选
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # 2. 创建日志记录器对象 -> 统一管理日志处理器，并设置日志级别
    logger = logging.getLogger('EduRAG')
    logger.setLevel(logging.INFO)
    # 核心: 判断处理器是否存在，避免多次调用函数导致重复添加
    if not logger.handlers:
        # 3. 创建控制台处理器 -> 用于将日志输出到控制台
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 4. 创建文件处理器 -> 用于将日志输出到文件
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 5. 创建日志输出格式
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # 6. 为两个处理器分别绑定日志格式
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # 7. 为日志记录器添加处理器，
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    # 8. 返回日志记录器
    return logger

# todo 3. 初始化日志器 -> 项目启动时自动执行, 其他模块导入此logger日志器即可直接使用
logger = setup_logger()