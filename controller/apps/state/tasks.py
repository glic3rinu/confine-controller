import requests, gevent
from celery.task import periodic_task
from celery.task.schedules import crontab
from gevent import monkey

from controller.utils import LockFile
from nodes.models import Node


def _ping(url):
    head = requests.head(url)
    return head


@periodic_task(name="state.ping", run_every=crontab(minute='*/5', hour='*'))
def ping():
    # Prevent concurrent executions
    # TODO calculate expire based on run_every
    with LockFile('/dev/shm/.state.ping.lock', expire=4*60):
        from .models import NodeState
        nodes = Node.objects.all()
        
        # enable async execution
        monkey.patch_all(thread=False, select=False)
        
        # create greenlets, with requests.get as a callback function
        glets = [ gevent.spawn(_ping, 'http://[%s]' % node.tinc.address) for node in nodes ]
        
        # wait for all greenlets to finish
        gevent.joinall(glets)
        
        # look at the results
        for node, glet in zip(nodes, glets):
            NodeState.store_glet(node, glet)
    
    return
