import requests
import gevent
from gevent import monkey


# Requirements:
# pip install requests
# apt-get install python-gevent

@task
def monitor(monitor):

    # create 200 grenlets.
    # each on is a call to requests.get
    monkey.patch_all(thread=False, select=False)
    url = 'http://www.google.com/%s'
    glets = [ gevent.spawn(requests.get, url % i, prefetch=True) for i in range(200) ]

    # wait for all the greenlets to finish
    gevent.joinall(glets)

    # look at the results
    for res in [glet.get() for glet in glets]:
        print res.content


def normal_get():
    url = 'http://www.google.com/%s'
    
    for url in [ url % i for i in range(200) ]:
        print requests.get(url).content
