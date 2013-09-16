from hirefire.procs.rq import RQProc
from redis import StrictRedis
from urlparse import urlparse
import os
redis_url = os.getenv('REDISGREEN_URL', 'redis://localhost:6379/')
u = urlparse(redis_url)


class WorkerProc(RQProc):
    name = 'worker'
    queues = ['high', 'default', 'low']
    connection = StrictRedis(host=u.hostname, port=u.port, db=0, password=u.password)
