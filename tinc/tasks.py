import os
from subprocess import Popen, PIPE

from celery.task import task

from nodes.models import Server

from .settings import TINC_HOSTS_PATH


@task(name="tinc.update_tincd")
def update_tincd():
    """
    Generates all local tinc/hosts/* and reloads tincd
    """
    from .models import TincClient
    server = Server.objects.get().tinc
    local_clients = TincClient.objects.filter(island__tincaddress__server=server)
    script = ''
    for client in local_clients:
        host_file = os.path.join(TINC_HOSTS_PATH, str(client.pk))
        script += 'echo "Subnet = %s" > %s;' % (client.subnet, host_file)
        script += 'echo "%s" >> %s;' % (client.pubkey, host_file)
    
    script += "/etc/init.d/tinc reload"
    cmd = Popen(script, shell=True, stdout=PIPE, stderr=PIPE)
    (stdout, stderr) = cmd.communicate()
    if cmd.returncode > 0:
        raise TincClient.UpdateTincdError(stderr)
