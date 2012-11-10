from datetime import datetime

from celery.task import periodic_task, task

from nodes.settings import CACHE_NODE_DB_CRONTAB


@periodic_task(name="nodes.periodic_cache_node_db", run_every=CACHE_NODE_DB_CRONTAB)
def periodic_cache_node_db():
    from nodes.models import Node
    for node in Node.objects.exclude(cndb_uri=""):
        node.cache_node_db()


@task(name="nodes.cache_node_db")
def cache_node_db(node_id):
    from nodes.models import Node
    node = Node.objects.get(pk=node_id)
    if node.cndb_uri:
        node.cndb_cached_on = datetime.now()
        node.save()
    return "NOT IMPLEMENTED"

