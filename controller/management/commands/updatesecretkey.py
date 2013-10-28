import os
from random import choice

from django.core.management.base import NoArgsCommand

from controller.utils import get_project_root
from controller.utils.system import run


class Command(NoArgsCommand):
    help = 'Update project SECRET_KEY setting.'
    
    def handle(self, *args, **options):
        context = {
            'key': ''.join([choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)]),
            'settings': os.path.join(get_project_root(), 'settings.py')}
        
        if run("grep 'SECRET_KEY' %(settings)s" % context, err_codes=[0,1]).return_code == 0:
            run("sed -i \"s/SECRET_KEY = '\w*'/SECRET_KEY = '%(key)s'/\" %(settings)s" % context)
        else:
            run("echo \"SECRET_KEY = '%(key)s'\" >> %(settings)s" % context)
