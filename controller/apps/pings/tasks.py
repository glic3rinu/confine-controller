import decimal
import subprocess
import os
from datetime import datetime

from celery.task import periodic_task, task
from celery.task.schedules import crontab
from django.db import transaction
from django.db.models import get_model
from django.utils import timezone

from controller.utils import LockFile
from controller.utils.apps import is_installed

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
        packet_loss = decimal.Decimal(stdout[-2].split(',')[2].split('%')[0])
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
        # Get the results
        for obj, coroutine in zip(objects, pool):
            result = coroutine.next()
            Ping.objects.create(content_object=obj, **result)
            coroutine.close()
    return len(objects)


@transaction.commit_on_success
def downsample(model):
    def aggregate(aggregated, slot_kwargs, minutes):
        THREEPLACES=decimal.Decimal('0.001')
        num_pings = len(aggregated)
        num_data = 0
        if num_pings > 1:
            min = avg = max = mdev = decimal.Decimal(0)
            packet_loss = 0
            for ping in aggregated:
                packet_loss += ping.packet_loss
                if ping.min:
                    min += ping.min
                    avg += ping.avg
                    max += ping.max
                    mdev += ping.mdev
                    num_data += 1
                ping.delete()
            kwargs = dict(slot_kwargs)
            # FIXME get the mean time instead
            kwargs['minute'] -= (minutes/2)
            ping = Ping(
                packet_loss=(packet_loss/num_pings),
                date=datetime(tzinfo=timezone.utc, **kwargs),
                content_object=ping.content_object)
            if num_data:
                ping.min = (min/num_data).quantize(THREEPLACES)
                ping.avg = (avg/num_data).quantize(THREEPLACES)
                ping.max = (max/num_data).quantize(THREEPLACES)
                # FIXME http://stats.stackexchange.com/questions/25848/how-to-sum-a-standard-deviation
                ping.mdev = (mdev/num_data).quantize(THREEPLACES)
            ping.save()
    
    def get_hourly_slot(ping, minutes):
        return {
            'year': ping.date.year,
            'month': ping.date.month,
            'day': ping.date.day,
            'hour': ping.date.hour,
            'minute': minutes-1,
            'second': datetime.max.second,
            'microsecond': datetime.max.microsecond
        }
    
    model = get_model(*model.split('.'))
    settings = Ping.get_instance_settings(model)
    downsamples = settings.get('downsamples')
    now = timezone.now()
    for obj in model.objects.all():
        end = None
        for downsample in downsamples:
            delta, minutes = downsample
            ini = now-delta
            pings = obj.pings.order_by('date').filter(date__lte=ini.strftime('%Y-%m-%d'))
            if end:
                pings = pings.filter(date__gt=end.strftime('%Y-%m-%d'))
            slot_kwargs = get_hourly_slot(pings[0], minutes)
            aggregated = []
            for ping in pings:
                slot_date = datetime(tzinfo=timezone.utc, **slot_kwargs)
                if ping.date <= slot_date:
                    aggregated.append(ping)
                else:
                    aggregate(aggregated, slot_kwargs, minutes)
                    aggregated = []
                    slot_kwargs['minute'] += minutes
                    if slot_kwargs['minute'] > 59:
                        slot_kwargs = get_hourly_slot(ping, minutes)
            aggregate(aggregated, slot_kwargs, minutes)
            end = ini


for instance in PING_INSTANCES:
    # Create periodic tasks
    hour = 2
    if is_installed(instance.get('app')):
        name = "pings.%s_ping" % instance.get('app')
        run_every = instance.get('schedule')
        
        @periodic_task(name=name, run_every=run_every, expires=run_every)
        def ping_instance(model=instance.get('model')):
            return ping(model)
        
#        name = "pings.%s_aggregate" % instance.get('app')
#        @periodic_task(name=name, run_every=crontab(minute=0, hour=hour))
#        def aggregate_pings(model=instance.get('model')):
#            return downsample(model)
        hour += 1
