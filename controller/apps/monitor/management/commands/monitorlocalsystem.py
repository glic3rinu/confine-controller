import os
import socket
import time
from optparse import make_option

from django.core.mail import mail_admins, get_connection
from django.core.management.base import BaseCommand

from monitor import settings
from monitor.models import TimeSerie


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--email', action='store_true', dest='email', default=False,
                help='Whether you want the problems reported on stdout or email'),
            make_option('--quiet', action='store_true', dest='quiet', default=False,
                help='Do not output anything'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Run monitors to diagnose system health.'
    
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
                # Send email if new alert or lock has expired
                send = True
                if os.path.exists(settings.MONITOR_ALERT_LOCK):
                    with open(settings.MONITOR_ALERT_LOCK, 'r') as lock_file:
                        if lock_file.readlines() == message.splitlines():
                            send = False
                    lock_time = os.path.getmtime(settings.MONITOR_ALERT_LOCK)
                    alert_expiration = settings.MONITOR_ALERT_EXPIRATION.total_seconds()
                    if time.time()-lock_time < alert_expiration:
                        send = False
                if send:
                    connection = get_connection(backend='django.core.mail.backends.smtp.EmailBackend')
                    connection.open()
                    mail_admins(subject , message, fail_silently=False, connection=connection)
                    connection.close()
                    with open(settings.MONITOR_ALERT_LOCK, 'w') as lock_file:
                        lock_file.write(message)
            if not email:
                self.stdout.write(message)
