import decimal
import math
import subprocess
import sys
import os

from celery.task import periodic_task, task
from celery.task.schedules import crontab
from django.db import transaction
from django.db.models import get_model
from django.utils import timezone

from controller.utils import LockFile
from controller.utils.apps import is_installed
from controller.utils.time import group_by_interval, get_sloted_start

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
        'version': 6 if ip.version() == 6 else ''
    }
    # Async execution of the ping command
    ping = subprocess.Popen("ping%(version)s -c %(count)s %(ip)s" % context,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=open('/dev/null', 'w'))
    yield
    ping.wait()
    if ping.returncode == 0:
        stdout = ping.stdout.readlines()
        ping.stdout.close()
        packet_loss = decimal.Decimal(stdout[-2].split(', ')[-2].split('%')[0])
        perf_type = ['min', 'avg', 'max', 'mdev']
        perf_data = stdout[-1].split(' ')[3].split('/')
        result = dict((k, decimal.Decimal(v)) for k,v in zip(perf_type, perf_data))
        result.update({'packet_loss': packet_loss})
        yield result
    ping.stdout.close()
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
        now = timezone.now()
        # Get the results
        for obj, coroutine in zip(objects, pool):
            result = coroutine.next()
            Ping.objects.create(content_object=obj, samples=PING_COUNT, date=now, **result)
            coroutine.close()
    return len(objects)


@transaction.atomic
def downsample(model):
    def aggregate(ping_set):
        THREEPLACES = decimal.Decimal('0.001')
        set_size = len(ping_set)
        aggregated = 0
        num_data = 0
        if set_size > 1:
            minimum = 0
            maximum = 0
            avg = decimal.Decimal(0)
            mdev = decimal.Decimal(0)
            packet_loss = 0
            samples = 0
            for ping in ping_set:
                ping_min = sys.maxint if ping.min is None else ping.min
                minimum = min(minimum, ping_min) or ping.min
                maximum = max(maximum, ping.max) or ping.max
                packet_loss += ping.packet_loss
                samples += ping.samples
                if ping.avg:
                    avg += ping.avg*ping.samples
                    # http://en.wikipedia.org/wiki/Standard_deviation#Sample-based_statistics
                    mdev += (ping.samples-1)*(ping.mdev**2) + ping.samples*(ping.avg**2)
                    num_data += ping.samples
                ping.delete()
                aggregated += 1
            packet_loss = packet_loss/set_size
            ping = Ping(samples=samples, packet_loss=packet_loss, date=ping.date,
                    content_object=ping.content_object)
            if num_data:
                avg = avg/num_data
                mdev = math.sqrt((mdev-(num_data*(avg**2))) / (num_data-1))
                ping.min = minimum.quantize(THREEPLACES)
                ping.max = maximum.quantize(THREEPLACES)
                ping.avg = avg.quantize(THREEPLACES)
                ping.mdev = round(mdev, 3)
            ping.save()
        return aggregated, set_size
    
    model = get_model(*model.split('.'))
    settings = Ping.get_instance_settings(model)
    downsamples = settings.get('downsamples')
    result = {
        'aggregated': 0,
        'created': 0,
        'total': 0,
    }
    now = timezone.now()
    for obj in model.objects.all():
        ini = None
        for downsample in downsamples:
            period, delta = downsample
            end = get_sloted_start(now-period, period)
            pings = obj.pings.order_by('date').filter(date__lte=end)
            if ini:
                pings = pings.filter(date__gt=ini)
            if pings:
                for __, ping_set in group_by_interval(pings, delta):
                    aggregated, set_size = aggregate(ping_set)
                    result['aggregated'] += aggregated
                    result['total'] += set_size
                    result['created'] += 1 if aggregated else 0
            ini = end
    return "(%(aggregated)s -> %(created)s) / %(total)s" % result


for instance in PING_INSTANCES:
    # get instance settings based on defaults
    settings = Ping.get_instance_settings(instance.get('model'))
    
    # Create periodic tasks
    hour = 2
    if is_installed(instance.get('app')) and settings.get('schedule') > 0:
        name = "pings.%s_ping" % instance.get('app')
        run_every = settings.get('schedule')
        
        @periodic_task(name=name, run_every=run_every, expires=run_every)
        def ping_instance(model=instance.get('model')):
            return ping(model)
        
        name = "pings.%s_downsample" % instance.get('app')
        @periodic_task(name=name, run_every=crontab(minute=0, hour=hour), time_limit=60*60*2)
        def downsample_pings(model=instance.get('model')):
            return downsample(model)
        hour += 1
