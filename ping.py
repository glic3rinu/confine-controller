import requests
import gevent
from gevent import monkey


def async_get(nodes):
    """
    requests.get() using Gevent
    
    Requirements:
       pip install requests
       apt-get install python-gevent
    """
    # enable async execution
    monkey.patch_all(thread=False, select=False)
    
    # create greenlets, with requests.get as a callback function
    glets = [ gevent.spawn(requests.get, 'http://[%s]/' % node.tinc.address, prefetch=True) for node in nodes ]

    # wait for all greenlets to finish
    gevent.joinall(glets)

    # look at the results    
    for glet, node in zip(glets, nodes):
        print node
        if glet.exception is not None:
            print glet.exception
        else:
            print glet.get().content
    return 
