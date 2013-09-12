from hirefire.procs.rq import RQProc
from redis import StrictRedis
from urlparse import urlparse
import os
redistogo_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379/')
u = urlparse(redistogo_url)


class WorkerProc(RQProc):
    name = 'worker'
    queues = ['high', 'default', 'low']
    connection = StrictRedis(host=u.hostname, port=u.port, db=0)