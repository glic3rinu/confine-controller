import requests
import gevent

from celery.task import task
from gevent import monkey

from nodes.models import Node

def ping(url):
    head = requests.head(url)
    return head


@task(name="monitor.monit")
def monit():
    from .models import TimeSerie
    nodes = Node.objects.all()
    
    # enable async execution
    monkey.patch_all(thread=False, select=False)
    
    # create greenlets, with requests.get as a callback function
    glets = [ gevent.spawn(ping, 'http://[%s]' % node.tinc.address) for node in nodes ]
    
    # wait for all greenlets to finish
    gevent.joinall(glets)
    
    # look at the results
    for node, glet in zip(nodes, glets):
        TimeSerie.store_glet(node, glet)
    return
