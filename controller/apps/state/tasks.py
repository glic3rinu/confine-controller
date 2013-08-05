import json
import os

import gevent
import requests, gevent
from celery.task import periodic_task, task
from django.db.models import get_model

from controller.utils import LockFile

from .settings import STATE_LOCK_DIR, STATE_NODESTATE_SCHEDULE, STATE_SLIVERSTATE_SCHEDULE


@task(name="state.get_state")
def get_state(state_module, ids=[], lock=True, patch=False):
    state_model = get_model(*state_module.split('.'))
    lock_file = os.path.join(STATE_LOCK_DIR, '.%s.lock' % state_model.__name__)
    freq = state_model.get_setting('SCHEDULE')
    # Prevent concurrent executions
    with LockFile(lock_file, expire=freq-(freq*0.2), unlocked=not lock):
        objects = state_model.objects.all()
        if ids:
            objects = objects.filter(pk__in=ids)
        
        # enable async execution (not needed since this is being executed in a gevent worker)
        if patch:
            gevent.monkey.patch_all(thread=False, select=False)
        
        glets = []
        for obj in objects:
            try:
                etag = json.loads(obj.metadata)['headers']['etag']
            except (ValueError, KeyError):
                headers = {}
            else:
                headers = {'If-None-Match': etag}
            glets.append(gevent.spawn(requests.get, obj.get_url(), headers=headers))
        
        # wait for all greenlets to finish
        gevent.joinall(glets)
        
        # look at the results
        for obj, glet in zip(objects, glets):
            state_model.store_glet(obj, glet)
    
    return len(objects)


@periodic_task(name="state.nodestate", run_every=STATE_NODESTATE_SCHEDULE,
               expires=STATE_NODESTATE_SCHEDULE)
def node_state():
    return get_state('state.NodeState')


@periodic_task(name="state.sliverstate", run_every=STATE_SLIVERSTATE_SCHEDULE,
               expires=STATE_SLIVERSTATE_SCHEDULE)
def sliver_state():
    return get_state('state.SliverState')
