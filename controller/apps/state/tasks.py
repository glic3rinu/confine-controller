import json
import os

import gevent
import requests, gevent
from celery.task import periodic_task, task
from django.db.models import get_model

from controller.utils import LockFile

from .models import State
from .settings import STATE_LOCK_DIR, STATE_NODE_SCHEDULE, STATE_SLIVER_SCHEDULE


@task(name="state.get_state")
def get_state(state_module, ids=[], lock=True, patch=False):
    model = get_model(*state_module.split('.'))
    lock_file = os.path.join(STATE_LOCK_DIR, '.%s.lock' % model.__name__)
    freq = State.get_setting(model, 'SCHEDULE')
    # Prevent concurrent executions
    with LockFile(lock_file, expire=freq-(freq*0.2), unlocked=not lock):
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


@periodic_task(name="state.node", run_every=STATE_NODE_SCHEDULE, expires=STATE_NODE_SCHEDULE)
def node_state():
    return get_state('nodes.Node')


@periodic_task(name="state.sliver", run_every=STATE_SLIVER_SCHEDULE, expires=STATE_SLIVER_SCHEDULE)
def sliver_state():
    return get_state('slices.Sliver')
