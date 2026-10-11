
import redis

r = redis.Redis(host='localhost', password='1234', port=6379, db=0)
r.flushdb()