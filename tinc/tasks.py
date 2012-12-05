from subprocess import Popen, PIPE

from celery.task import task

from nodes.models import Server

from .settings import TINC_NET_NAME


@task(name="tinc.update_tincd")
def update_tincd():
    """
    Generates all local tinc/hosts/* and reloads tincd
    """
    from .models import TincClient
    
    # TODO delete deprectaed clients (tinc hosts)
    server = Server.objects.get().tinc
    local_clients = TincClient.objects.filter(island__tincaddress__server=server)
    script = ''
    for client in local_clients:
        host_file = '/etc/tinc/%s/hosts/%s' % (TINC_NET_NAME, client.pk)
        script += 'echo -e "Subnet = %s\n" > %s;' % (client.subnet, host_file)
        script += 'echo "%s" >> %s;' % (client.pubkey, host_file)
    
    if script != '':
        script += "/etc/init.d/tinc reload"
        cmd = Popen(script, shell=True, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = cmd.communicate()
        if cmd.returncode > 0:
            raise TincClient.UpdateTincdError(stderr)
