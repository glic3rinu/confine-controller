import decimal
import subprocess
import os
from datetime import datetime

from celery.task import periodic_task, task
from django.db.models import get_model

from controller.utils import LockFile, is_installed

from .models import Ping
from .settings import PING_LOCK_DIR, PING_COUNT, PING_INSTANCES


def pinger(ip):
    """
    Two-phase ping coroutine
    phase one: spawn a ping process and yield
    phase two: wait until ping finishes, then process stdout and yield the result
    """
    context = {
        'ip': ip,
        'count': PING_COUNT,
        'version': 6 if ip.version() == 6 else '' }
    # Async execution of the ping command
    ping = subprocess.Popen("ping%(version)s -c %(count)s %(ip)s" % context,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=open('/dev/null', 'w'))
    yield
    ping.wait()
    if ping.returncode == 0:
        stdout = ping.stdout.readlines()
        packet_loss = decimal.Decimal(stdout[-2].split(',')[2].split('%')[0])
        perf_type = ['min', 'avg', 'max', 'mdev']
        perf_data = stdout[-1].split(' ')[3].split('/')
        result = dict((k, decimal.Decimal(v)) for k,v in zip(perf_type, perf_data))
        result.update({'packet_loss': packet_loss})
        yield result
    yield {'packet_loss': 100}


@task(name="pings.ping")
def ping(model, ids=[], lock=True):
    """
    Ping task based on cooperative multitasking model
    ICMP sockets can only be used by privileged users, so we have decided to use
    the OS ping command (has suid) in order to avoid running this task as root.
    This coroutine solution outperforms thread pool concurrency pattern :)
    """
    model = get_model(*model.split('.'))
    lock_file = os.path.join(PING_LOCK_DIR, '.%s.lock' % model.__name__)
    
    settings = Ping.get_instance_settings(model)
    if settings is None:
        raise AttributeError('Unknown model %s' % str(model))
    freq = settings.get('schedule')
    get_addr = settings.get('get_addr')
    
    # Prevent concurrent executions
    with LockFile(lock_file, expire=freq-(freq*0.2), unlocked=not lock):
        objects = model.objects.all()
        filter = settings.get('filter', False)
        if filter:
            objects = objects.filter(**filter)
        if ids:
            objects = objects.filter(id__in=ids)
        
        # Create pool and spawn some process
        pool = []
        for obj in objects:
            coroutine = pinger(get_addr(obj))
            coroutine.next()
            pool.append(coroutine)
        # Get the results
        for obj, coroutine in zip(objects, pool):
            result = coroutine.next()
            Ping.objects.create(content_object=obj, **result)
            coroutine.close()
    
    return len(objects)


for instance in PING_INSTANCES:
    # Create periodic tasks
    if is_installed(instance.get('app')):
        name = "pings.%s_ping" % instance.get('app')
        run_every = instance.get('schedule')
        
        @periodic_task(name=name, run_every=run_every, expires=run_every)
        def ping_instance(model=instance.get('model')):
            return ping(model)
