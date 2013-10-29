import json
import os

import gevent
import requests
from celery.task import periodic_task, task
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


