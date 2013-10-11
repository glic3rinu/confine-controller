import json
import time
from datetime import timedelta

from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.management import call_command
from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse

from controller.admin.utils import get_modeladmin, wrap_admin_view
from controller.utils.time import group_by_interval
from nodes.models import Server

from . import settings
from .models import TimeSerie


def monitor_view(request):
    call_command('monitorlocalsystem', email=True, quiet=True)
    monitors = TimeSerie.get_monitors()
    context = {
        "title": "Server monitoring summary",
        'monitors': monitors,
        'opts': Server._meta,
        'base_url': '/admin/nodes/server/monitor',
    }
    return TemplateResponse(request, 'admin/monitor/monitoring.html', context,
            current_app='monitor')


def factor(value, divisor):
    return int(value)/divisor if value else value

def TimeSerie_view(request, name):
    data = []
    try:
        monitor = TimeSerie.get_monitor(name)
    except KeyError:
        raise Http404
    series = monitor.series.order_by('date')
#    series = series.extra(select={'date': "EXTRACT(EPOCH FROM date)"}).values('date', 'value')
    previous = None
    for __,series in group_by_interval(series, timedelta(minutes=5)):
        serie = monitor.aggregate(series)
        serie.apply_relativity(previous)
        previous = serie
        date = int(serie.date.strftime('%s').split('.')[0] + '000')
        data.append([date, serie.value])
    return HttpResponse(json.dumps(data), content_type="application/json")


ServerAdmin = get_modeladmin(Server)
old_server_get_urls = ServerAdmin.get_urls
def get_urls():
    urls = old_server_get_urls()
    extra_urls = patterns("",
        url("^monitor/(?P<name>\w+)",
            wrap_admin_view(ServerAdmin, TimeSerie_view),
            name='nodes_server_monitor_netio'),
        url("^monitor",
            wrap_admin_view(ServerAdmin, monitor_view),
            name='nodes_server_monitor'),
        )
    return extra_urls + urls
ServerAdmin.get_urls = get_urls
