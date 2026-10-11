# 该文件用于帮助 mysql_qa 这个 Python 包，管理包内的脚本，方便其它包的调用。

import os, sys

# 1. 记录当前目录
current_dir = os.path.abspath(__file__)

# 2. 记录 mysql_qa 目录
mysql_qa_path = os.path.dirname(current_dir)

# 3. 添加 mysql_qa_path 路径到系统路径变量中
sys.path.insert(0, mysql_qa_path)

# 4. 具体导包
from db.mysql_client import MySQLClient
from cache.redis_client import RedisClient
from retrieval.bm25_search import BM25Search
