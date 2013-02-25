from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from controller.utils import update_settings
from controller.utils.system import run, check_root, get_default_celeryd_username


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--username', dest='username', default=get_default_celeryd_username(),
                help='Specifies the system user that would generate the firmwares.'),
            make_option('--base_image_path', dest='base_image_path', default=False,
                help='Specifies the path where the base images are stored.'),
            make_option('--build_path', dest='base_path', default=False,
                help='Specifies the path where the build images are stored.'),
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
        
        if run('grep "^fuse:" /etc/group', err_codes=[0,1]).return_code == 1:
            run('addgroup fuse')
        if run('groups %s|grep fuse' % username, err_codes=[0,1]).return_code == 1: 
            run('adduser %s fuse' % username)
        
        base_image_path = options.get('base_image_path')
        if base_image_path:
            update_settings(FIRMWARE_BASE_IMAGE_PATH=base_image_path)
        
        build_path = options.get('build_path')
        if build_path:
            update_settings(FIRMWARE_BUILD_PATH=build_path)
