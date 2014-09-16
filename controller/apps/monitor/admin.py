import json
from datetime import timedelta, datetime

from django.conf.urls import patterns, url
from django.core.management import call_command
from django.http import HttpResponse, Http404
from django.utils import timezone
from django.template.response import TemplateResponse

from controller.admin.utils import get_modeladmin, wrap_admin_view
from controller.utils.time import group_by_interval
from nodes.models import Server

from .models import TimeSerie


def monitor_view(request):
    call_command('monitorlocalsystem', email=True, quiet=True)
    monitors = TimeSerie.get_monitors()
    context = {
        "title": "Server monitoring summary",
        'monitors': monitors,
        'opts': Server._meta,
        'base_url': '/admin/nodes/server/monitor',
        'querystring': '?' + '&'.join(['%s=%s' % (k,v) for k,v in request.GET.items()])
    }
    return TemplateResponse(request, 'admin/monitor/monitoring.html', context,
            current_app='monitor')


def time_serie_view(request, name):
    raw = request.GET.get('raw', False)
    date_from = request.GET.get('from', False)
    date_to = request.GET.get('to', False)
    data = []
    try:
        monitor = TimeSerie.get_monitor(name)
    except KeyError:
        raise Http404
    series = monitor.series.order_by('date')
    if date_from and date_to:
        date_from = datetime.fromtimestamp(float(date_from), timezone.utc)
        date_to = datetime.fromtimestamp(float(date_to), timezone.utc)
        series = series.filter(date__gte=date_from, date__lte=date_to)
    if raw and raw.capitalize() == 'True':
        series = [ [False, [serie]] for serie in series ]
    else:
        series = group_by_interval(series, timedelta(minutes=5))
    previous = None
    for __, series in series:
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
            wrap_admin_view(ServerAdmin, time_serie_view),
            name='nodes_server_monitor_netio'),
        url("^monitor",
            wrap_admin_view(ServerAdmin, monitor_view),
            name='nodes_server_monitor'),
        )
    return extra_urls + urls
ServerAdmin.get_urls = get_urls
