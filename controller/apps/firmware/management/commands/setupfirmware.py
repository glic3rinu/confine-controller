from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from common.system import run, check_root


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--username', dest='username', default=get_default_celeryd_username(),
                help='Specifies the system user that would generate the firmwares.'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind. '
                     'You must use --username with --noinput, and must contain the '
                     'cleeryd process owner, which is the user how will perform tincd updates'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Prepare the system for generating firmware in userspace.'
    
    
    @check_root
    def handle(self, *args, **options):
        # Configure firmware generation
        username = options.get('username')
        if username is None:
            raise CommandError('Can not find default celeryd username')
        
        run('addgroup fuse')
        run('adduser %s fuse' % username)
