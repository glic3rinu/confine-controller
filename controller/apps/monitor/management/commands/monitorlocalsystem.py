import json
import re
import socket
from optparse import make_option

from django.core.mail import mail_admins, get_connection
from django.core.management.base import BaseCommand

from monitor import settings
from monitor.models import TimeSerie


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--email-report', action='store_true', dest='email', default=False,
                help='Wheter you want the probelms reported on stdout or email'),
            make_option('--quiet', action='store_true', dest='quiet', default=False,
                help='Do not output anything'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Run monitors.'
    
    def handle(self, *args, **options):
        problems = []
        
        for monitor in TimeSerie.get_monitors():
            value, current_problems = monitor.execute()
            problems += current_problems
            monitor.store(value)
        
        quiet = options.get('quiet')
        email = options.get('email')
        
        if not quiet:
            if problems:
                subject = 'Problems detected on %s' % socket.gethostname()
                problems = '\n    * '.join(problems)
                message = 'The following problems have been detected:\n    * %s' % problems
            else:
                message = 'No problems detected'
            if problems and email:
                connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
                connection.open()
                mail_admins(subject , message, fail_silently=False, connection=connection)
                connection.close()
            if not email:
                self.stdout.write(message)
