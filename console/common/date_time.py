# -*- coding: utf8 -*-

import time
import pytz
import dateutil
import calendar
import datetime
from django.conf import settings
from django.utils.timezone import localtime
from django.utils import timezone


def to_timestamp(utc_dt):
    if not utc_dt:
        return utc_dt
    return calendar.timegm(utc_dt.utctimetuple())


def to_local_str(dt, fmt='%Y-%m-%d %H:%M:%S'):
    local_dt = localtime(dt, timezone=pytz.timezone(settings.TIME_ZONE))
    return local_dt.strftime(fmt)


def ts_to_cn(ts):
    return datetime.fromtimestamp(ts, pytz.timezone(settings.TIME_ZONE))


def before_to_now(days):
    now = timezone.now()
    for num in xrange(days, 0, -1):
        dt = now - datetime.timedelta(days=num)
        yield dt


def str_to_timestamp(dt_str, fmt='%Y-%m-%d %H:%M:%S'):
    return to_timestamp(dateutil.parser.parse(dt_str))


class Timer:

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start

    def __unicode__(self):
        return '%.5f' % self.interval

    def __str__(self):
        return '%.5f' % self.interval


def get_utc_time():
    from django.utils.timezone import now
    return now()


def now_to_timestamp(convert_to_utc=False):
    now = datetime.datetime.now()
    timestamp = datetime_to_timestamp(now, convert_to_utc=convert_to_utc)
    return int(timestamp)


# convert time to timestamp
def datetime_to_timestamp(sample, convert_to_utc=False):
    if isinstance(sample, datetime.datetime):
        if convert_to_utc:
            sample = sample + datetime.timedelta(hours=-8)
            # FixMe: hour=-8
        return time.mktime(sample.timetuple())
    elif isinstance(sample, basestring):
        _datetime = dateutil.parser.parse(sample)
        if convert_to_utc:
            _datetime = _datetime + datetime.timedelta(hours=-8)
        if _datetime:
            return time.mktime(_datetime.timetuple())
    else:
        return None
