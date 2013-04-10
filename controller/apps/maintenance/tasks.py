import socket
from datetime import datetime

import paramiko
from celery.task import task

from .settings import MAINTENANCE_KEY_PATH


@task(name="maintenance.run_instance")
def run_instance(instance_id):
    from .models import Instance
    instance = Instance.objects.get(pk=instance_id)
    if not instance.execution.is_active:
        return 'no active'
    instance.state = Instance.STARTED
    instance.last_try = datetime.now()
    instance.save()
    try:
        # ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        addr = str(instance.node.mgmt_net.addr)
        try:
            ssh.connect(addr, username='root', key_filename=MAINTENANCE_KEY_PATH)
        except socket.error:
            instance.state = Instance.TIMEOUT
            instance.save()
            return 'socket error'
        channel = ssh.get_transport().open_session()
        channel.exec_command(instance.script)
        #stderr = channel.recv_stderr(1024)
        instance.stdout = ''.join(channel.makefile('rb', -1).readlines())
        instance.stderr = ''.join(channel.makefile_stderr('rb', -1).readlines())
        instance.exit_code = exit_code = channel.recv_exit_status()
        instance.state = Instance.SUCCESS if exit_code == 0 else Instance.FAILURE
        channel.close()
        ssh.close()
        instance.save()
    except:
        instance.state = Instance.FAILURE
        instance.save()
        raise
