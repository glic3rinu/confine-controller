from celery.task import periodic_task, task
from nodes.settings import CACHE_NODE_DB_CRONTAB


@periodic_task(name="Cache NodeDB", run_every=CACHE_NODE_DB_CRONTAB)
def periodic_cache_node_db():
    # Avoid circular import
    from nodes.models import Node
    for node in Node.objects.filter(nodedb_uri__not=""):
        node.cache_node_db()


@task(name="Cache NodeDB")
def cache_node_db(node_id):
    from nodes.models import Node
    node = Node.objects.get(pk=node_id)
    return "NOT IMPLEMENTED"

