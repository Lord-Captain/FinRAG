'''
该脚本用于验证Milvus和Redis服务是否成功
'''
# todo 1. 测试Milvus服务是否正常
from pymilvus import connections, utility

# 1. 建立与Milvus服务的连接
# 参1(host): 代表本机地址，仅本机程序能访问数据库
# 参2(port): 代表Milvus服务端口
connections.connect(host='127.0.0.1', port='19530') # 这里要等Milvus启动1-2分钟后再执行，否则会报错连接失败

# 2. 获取并打印Milvus服务端版本号
print(f'Milvus version: {utility.get_server_version()}')    # Milvus version: v2.4.4

# todo 2. 测试redis服务是否成功
import redis
# 1. 创建Redis客户端实例，用于与Redis服务建立连接并执行操作
client = redis.Redis(
    host = 'localhost',     # Redis服务器的主机地址，如果Redis在其他机器，写对应的IP即可
    port = 6379,            # Redis服务器端口号
    password = '1234',      # Redis数据库的索引
    decode_responses=True   # 是否对返回的数据进行解码为字符串，默认为True
)

# 2. 测试Redis连接是否正常，通过设置和获取键值对验证
try:
    # 2.1 通过set()方法，设置1组键值对
    client.set('name', '张三')
    # 2.2 用get()方法获取键值对的值
    value = client.get('name')
    print(value)
except Exception as e:
    print(f'连接失败, 原因是:{e}')