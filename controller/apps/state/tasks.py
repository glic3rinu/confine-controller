import json
import os

import gevent
import requests
from celery.task import periodic_task, task
from django.contrib.contenttypes.models import ContentType
from django.db.models import get_model

from controller.utils import LockFile

from .settings import STATE_LOCK_DIR, STATE_SCHEDULE


@task(name="state.get_state")
def get_state(state_module, ids=[], lock=True, patch=False):
    from .models import State
    lock_file = os.path.join(STATE_LOCK_DIR, '.%s.lock' % state_module)
    freq = STATE_SCHEDULE
    # Prevent concurrent executions
    with LockFile(lock_file, expire=freq-(freq*0.2), unlocked=not lock):
        model = get_model(*state_module.split('.'))
        objects = model.objects.all()
        if ids:
            objects = objects.filter(pk__in=ids)
        
        # enable async execution (not needed since this is being executed in a gevent worker)
        if patch:
            gevent.monkey.patch_all(thread=False, select=False)
        
        glets = []
        for obj in objects:
            try:
                etag = json.loads(obj.state.metadata)['headers']['etag']
            except (ValueError, KeyError):
                headers = {}
            else:
                headers = {'If-None-Match': etag}
            glets.append(gevent.spawn(requests.get, obj.state.get_url(), headers=headers))
        
        # wait for all greenlets to finish
        gevent.joinall(glets)
        
        # look at the results
        for obj, glet in zip(objects, glets):
            State.store_glet(obj, glet)
    return len(objects)


@periodic_task(name="state.node", run_every=STATE_SCHEDULE, expires=STATE_SCHEDULE)
def node_state():
    return get_state('nodes.Node')


@periodic_task(name="state.sliver", run_every=STATE_SCHEDULE, expires=STATE_SCHEDULE)
def sliver_state():
    return get_state('slices.Sliver')


REPORT_NODE_STATES = (
    ('online', ['production']),
    ('unknown', ['unknown', 'nodata']),
    ('offline', ['debug', 'safe', 'offline', 'crashed', 'failure']),
)

REPORT_SLIVER_STATES = (
    ('sliver_registered', 'registered'),
    ('sliver_started', 'started'),
    ('sliver_deployed', 'deployed'),
)

@periodic_task(name="state.report", run_every=STATE_SCHEDULE, expires=STATE_SCHEDULE)
def update_state_report():
    """ Update Reports with aggregated data of nodes/slivers state """
    from slices.models import Slice
    from users.models import Group
    from .models import Report, State

    ct_node = ContentType.objects.get(name='node')
    qs_nodes = State.objects.filter(content_type=ct_node,
                    node__group__isnull=False)
    ct_sliver = ContentType.objects.get(name='sliver')
    qs_slivers = State.objects.filter(content_type=ct_sliver)

    qs_slices = Slice.objects.all()
    for group in Group.objects.all():
        value = _get_aggregated_data(qs_nodes, qs_slivers, qs_slices, group)
        report, created = Report.objects.get_or_create(group=group)
        report.value = value
        report.save()

    # TOTAL AGGREGATION: create a special report for all the groups together
    value = _get_aggregated_data(qs_nodes, qs_slivers, qs_slices)
    report, created = Report.objects.get_or_create(group=None)
    report.value = value
    report.save()

def _get_aggregated_data(qs_nodes, qs_slivers, qs_slices, group=None):
    value = {}
    
    if group is not None:
        qs_nodes = qs_nodes.filter(node__group=group)
        qs_slivers = qs_slivers.filter(sliver__slice__group=group)
        qs_slices = qs_slices.filter(group=group)
    
    # get nodes info
    for key, states in REPORT_NODE_STATES:
        value[key] = qs_nodes.filter(value__in=states).count()
    value['total'] = qs_nodes.count()
    
    # get slivers info
    for key, state in REPORT_SLIVER_STATES:
        value[key] = qs_slivers.filter(value=state).count()
    value['sliver_total'] = qs_slivers.count()
    
    # get slices info
    value['slices'] = qs_slices.count()
    
    return value
