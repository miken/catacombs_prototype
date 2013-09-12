from hirefire.procs.rq import RQProc
from redis import StrictRedis


class WorkerProc(RQProc):
    name = 'worker'
    queues = ['high', 'default', 'low']
    connection = StrictRedis('localhost', 6379, db=0)