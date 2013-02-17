import os, glob, time

from celery.task import task

from controller.utils import LockFile
from controller.utils.system import run, touch
from nodes.models import Server

from .settings import TINC_NET_NAME


@task(name="tinc.update_tincd")
def update_tincd():
    """
    Generates all local tinc/hosts/* and reloads tincd
    """
    from .models import TincClient
    
    hosts_path = '/etc/tinc/%s/hosts/' % TINC_NET_NAME
    
    # Dirty mechanism to know if there has been any change while running
    dirtyfile = os.path.join(hosts_path, '.dirty')
    now = time.time()
    touch(dirtyfile, times=(now, now))
    
    # File-based lock mechanism to prevent concurrency problems
    lock = LockFile(hosts_path+'.lock', expire=60)
    if lock.acquire():
        try:
            # TODO generate also TincServers/Gateways on tinc/hosts ??
            server = Server.objects.get().tinc
            clients = TincClient.objects.all()
            
            # Batch processing of tinc clients for efficiency/max_arg_length tradeoff
            scripts = []
            total = clients.count()
            for start in range(0, total, 100):
                end = min(start + 100, total)
                script = ''
                for client in clients[start:end]:
                    host_file = os.path.join(hosts_path, client.name)
                    script += 'echo -e "%s" > %s;\n' % (client.get_host(), host_file)
                scripts.append(script)
            
            # delete all tinc hosts
            run('rm %s{host_,node_}*' % hosts_path, err_codes=[0,1])
            
            # create all tinc hosts
            for script in scripts:
                run(script)
        finally:
            # always release the lock
            lock.release()
        
        # retry if there is any pending modification
        if os.path.getmtime(dirtyfile) > now:
            raise update_tincd.retry(countdown=1)
        
        run("/etc/init.d/tinc reload", silent=False)
