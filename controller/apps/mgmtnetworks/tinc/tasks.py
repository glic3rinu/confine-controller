import os, glob, time

from celery.task import task

from controller.utils import LockFile
from controller.utils.system import run, touch

from .settings import TINC_NET_NAME, TINC_TINCD_ROOT


@task(name="tinc.update_tincd")
def update_tincd():
    """
    Generates all local tinc/hosts/* and reloads tincd
    """
    from .models import TincClient, TincServer
    
    hosts_path = '%s/hosts/' % os.path.join(TINC_TINCD_ROOT, TINC_NET_NAME)
    
    # Dirty mechanism to know if there has been any change while running
    dirtyfile = os.path.join(hosts_path, '.dirty')
    now = time.time()
    touch(dirtyfile, times=(now, now))
    
    # File-based lock mechanism to prevent concurrency problems
    with LockFile(hosts_path+'.lock', expire=60):
        clients = TincClient.objects.all()
        gateways = TincServer.objects.gateways()
        hosts = list(clients) + list(gateways)
        # Batch processing of tinc clients for efficiency/max_arg_length tradeoff
        scripts = []
        total = len(hosts)
        for start in range(0, total, 100):
            end = min(start + 100, total)
            script = ''
            for host in hosts[start:end]:
                host_file = os.path.join(hosts_path, host.name)
                script += 'echo -e "%s" > %s;\n' % (host.get_host(), host_file)
            scripts.append(script)
        
        # delete all tinc hosts
        run('rm -f -- %s{host_,node_}*' % hosts_path)
        
        # create all tinc hosts
        for script in scripts:
            run(script)
    
    # retry if there is any pending modification
    if os.path.getmtime(dirtyfile) > now:
        raise update_tincd.retry(countdown=1)
    
    run("/etc/init.d/tinc reload", silent=False)
