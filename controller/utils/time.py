from __future__ import absolute_import

from datetime import datetime
from time import mktime

from django.utils.timesince import timesince as django_timesince
from django.utils.timezone import is_aware, utc


def timesince(d, now=None, reversed=False):
    """ Hack to provide second precision under 2 minutes """
    if not now:
        now = datetime.now(utc if is_aware(d) else None)
    
    delta = (d - now) if reversed else (now - d)
    s = django_timesince(d, now=now, reversed=reversed)
    
    if len(s.split(' ')) is 2:
        count, name = s.split(' ')
        if name in ['minutes', 'minute']:
            seconds = delta.seconds % 60
            extension = '%(number)d %(type)s' % {'number': seconds, 'type': 'seconds'}
            if int(count) is 0:
                return extension
            elif int(count) < 2:
                s += ', %s' % extension
    return s


def timeuntil(d, now=None):
    """
    Like timesince, but returns a string measuring the time until
    the given time.
    """
    return timesince(d, now, reversed=True)


def heartbeat_expires(date, freq, expire_window):
    timestamp = mktime(date.timetuple())
    return timestamp + freq * (expire_window / 1e2)


def get_sloted_start(initial, delta):
    if not isinstance(initial, datetime):
        initial = datetime.fromtimestamp(initial, utc)
    if not isinstance(delta, int) and not isinstance(delta, float):
        # Works with timedelta and relativedelta
        delta = int(initial.strftime('%s')) - int((initial-delta).strftime('%s'))
    kwargs = {
        'year': initial.year,
        'month': 1,
        'day': 1
    }
    if delta < 60*60*24:
        kwargs['day'] = initial.day
    if delta < 60*60:
        kwargs['hour'] = initial.hour
    if delta < 60*60*24*364:
        kwargs['month'] = initial.month
    return datetime(tzinfo=utc, **kwargs)


def group_by_interval(series, delta, fill_empty=False, key=lambda s: s.date):
    initial = key(series[0])
    isdatetime = isinstance(initial, datetime)
    if not isdatetime:
        initial = datetime.fromtimestamp(initial, utc)
    if not isinstance(delta, int):
        delta = delta.total_seconds()
    
    ini = float(get_sloted_start(initial, delta).strftime('%s'))
    end = ini+delta
    group = []
    timestamp = 0
    num = 0
    for serie in series:
        date = key(serie)
        if isdatetime:
            date = float(date.strftime('%s'))
        if date > ini and date <= end:
            timestamp += date
            group.append(serie)
            num += 1
        elif date > end:
            while date > end:
                ini = end
                end += delta
                if group:
                    timestamp = timestamp/num
                else:
                    if num == 0 or not fill_empty:
                        continue
                    timestamp = (end+ini)/2
                if isdatetime:
                    timestamp = datetime.fromtimestamp(timestamp, utc)
                yield (timestamp, group)
                group = []
            group = [serie]
            timestamp = date
            num = 1
        else:
            raise NotImplementedError('Only ordered lists are supported')
    if group:
        timestamp = timestamp/num
        if isdatetime:
            timestamp = datetime.fromtimestamp(timestamp, utc)
        yield (timestamp, group)
