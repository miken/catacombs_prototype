from hirefire.procs.rq import RQProc
from redis import StrictRedis
from urlparse import urlparse
import os
rediscloud_url = os.getenv('REDISCLOUD_URL', 'redis://localhost:6379/')
u = urlparse(rediscloud_url)


class WorkerProc(RQProc):
    name = 'worker'
    queues = ['high', 'default', 'low']
    connection = StrictRedis(host=u.hostname, port=u.port, password=u.password)
