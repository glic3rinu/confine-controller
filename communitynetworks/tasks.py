from datetime import datetime

from celery.task import periodic_task, task

from .settings import CACHE_NODE_DB_CRONTAB


@periodic_task(name="communitynetworks.periodic_cache_node_db", run_every=CACHE_NODE_DB_CRONTAB)
def periodic_cache_node_db():
    from .models import CnHost
    for host in CnHost.objects.exclude(cndb_uri=""):
        host.cache_node_db()
    return "NOT IMPLEMENTED"


@task(name="communitynetworks.cache_node_db")
def cache_node_db(obj):
    from .models import CnHost
    fresh_obj = type(obj).objects.get(pk=obj.pk)
    if fresh_obj.cndb_uri:
        fresh_obj.cndb_cached_on = datetime.now()
        fresh_obj.save()
    return "NOT IMPLEMENTED"

