from hirefire.procs.rq import RQProc
from redis import Redis


class WorkerProc(RQProc):
    name = 'worker'
    queues = ['high', 'default', 'low']
    connection = Redis('my.host.org', 6379)