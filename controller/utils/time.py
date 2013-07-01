from __future__ import absolute_import

import datetime
from time import mktime

from django.utils.timesince import timesince as django_timesince
from django.utils.timezone import is_aware, utc


def timesince(d, now=None, reversed=False):
    """ Hack to provide second precission under 2 minutes """
    if not now:
        now = datetime.datetime.now(utc if is_aware(d) else None)
    
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
