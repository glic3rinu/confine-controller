import requests, gevent, os
from celery.task import periodic_task
from django.db.models import get_model
from gevent import monkey

from controller.utils import LockFile

from .settings import STATE_LOCK_DIR, STATE_NODESTATE_SCHEDULE, STATE_SLIVERSTATE_SCHEDULE


def get_state(state_module):
    state_model = get_model(*state_module.split('.'))
    lock_file = os.path.join(STATE_LOCK_DIR, '.%s.lock' % state_model.__name__)
    freq = state_model.get_setting('SCHEDULE')

    # Prevent concurrent executions
    with LockFile(lock_file, expire=freq-(freq*0.2)):
        objects = state_model.get_related_model().objects.all()
        URI = state_model.get_setting('URI')
        node = lambda obj: getattr(obj, 'node', obj)
        
        # enable async execution
        monkey.patch_all(thread=False, select=False)
        
        # create greenlets
        glets = [ gevent.spawn(requests.get, URI % {'mgmt_addr': node(obj).mgmt_net.addr,
                                                    'object_id': obj.pk, }) for obj in objects ]
        
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
