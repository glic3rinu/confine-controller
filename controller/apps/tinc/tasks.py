import os
import time

from celery.task import task

from controller.utils import LockFile
from controller.utils.system import run, touch

from .settings import TINC_NET_NAME, TINC_TINCD_ROOT, TINC_TINCD_BIN, TINC_TINCD_SEND_HUP


@task(name="tinc.update_tincd")
def update_tincd():
    """
    Generates all local tinc/hosts/* and reloads tincd
    """
    from .models import TincHost
    
    hosts_path = '%s/hosts/' % os.path.join(TINC_TINCD_ROOT, TINC_NET_NAME)
    
    # Dirty mechanism to know if there has been any change while running
    dirtyfile = os.path.join(hosts_path, '.dirty')
    now = time.time()
    touch(dirtyfile, times=(now, now))
    
    # File-based lock mechanism to prevent concurrency problems
    with LockFile(hosts_path+'.lock', expire=60):
        hosts = TincHost.objects.hosts() # clients
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
    
    # In some systems it is mandatory to send a HUP signal in order to reload new subnets
    if TINC_TINCD_SEND_HUP:
        context = {
            'tincd_bin': TINC_TINCD_BIN,
            'net_name': TINC_NET_NAME
        }
        tinc_hup = "sudo %(tincd_bin)s -kHUP -n %(net_name)s" % context
        run(tinc_hup)
