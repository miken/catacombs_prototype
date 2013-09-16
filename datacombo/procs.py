from hirefire.procs.rq import RQProc
import redis
import os
redis_url = os.getenv('REDISGREEN_URL', 'redis://localhost:6379/')


class WorkerProc(RQProc):
    name = 'worker'
    queues = ['high', 'default', 'low']
    connection = redis.from_url(redis_url)
