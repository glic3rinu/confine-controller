import socket, sys

import paramiko
from celery.datastructures import ExceptionInfo
from celery.task import task
from django.utils.timezone import now

from controller.apps.maintenance.settings import MAINTENANCE_KEY_PATH

def run_cmd(cmd):
    # ssh connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("fdf5:5351:1dfd:7:0:0:0:2", username='root', key_filename=MAINTENANCE_KEY_PATH)
    channel = ssh.get_transport().open_session()
    channel.exec_command(cmd)
    #stderr = channel.recv_stderr(1024)
    print channel.makefile('rb', -1).read()
    print channel.makefile_stderr('rb', -1).read()
    print channel.recv_exit_status()
    channel.close()
    ssh.close()
