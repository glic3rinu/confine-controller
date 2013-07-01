from threading import Thread
import subprocess
from Queue import Queue
from nodes.models import Node

num_threads = 100
queue = Queue()


def pinger(i, q):
    """Pings subnet"""
    while True:
        ip = q.get()
        print "Thread %s: Pinging %s" % (i, ip)
        ret = subprocess.call("ping6 -c 4 %s" % ip,
                shell=True,
                stdout=open('/dev/null', 'w'),
                stderr=subprocess.STDOUT)
        if ret == 0:
            print "%s: is alive" % ip
        else:
            print "%s: did not respond" % ip
        q.task_done()


for i in range(num_threads):
    worker = Thread(target=pinger, args=(i, queue))
    worker.setDaemon(True)
    worker.start()


#Place work in queue
for ip in [str(node.mgmt_net.addr) for node in Node.objects.all()]:
    queue.put(ip)


queue.join()

