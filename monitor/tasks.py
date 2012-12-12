import requests
import gevent
from gevent import monkey


def async_get(nodes, faulty):
    """
    requests.get() using Gevent

    Requirements:
       pip install requests
       apt-get install python-gevent
    """
    # enable async execution
    monkey.patch_all(thread=False, select=False)
    
    # create greenlets, with requests.get as a callback function
    glets = [ gevent.spawn(requests.get, 
              'http://www.google.com/%s' % i, 
              prefetch=True) for i in range(nodes) ]

    glets.extend([ gevent.spawn(requests.get, 
                   'http://12.2.21.2/%s' % i, 
                   prefetch=True) for i in range(faulty) ])

    # wait for all greenlets to finish
    gevent.joinall(glets)

    # look at the results    
    for res in [glet.get() for glet in glets]:
        res.content
    return 


def normal_get(nodes, faulty):
    """
    traditional requests.get()
    """

    # generate urls
    urls = [ 'http://www.google.com/%s' % i for i in range(nodes) ]
    urls.extend([ 'http://12.2.21.2/%s' % i for i in range(faulty) ])

    # make the requests
    for url in urls:
        try: requests.get(url).content
        except requests.exceptions.ConnectionError: pass
    return
