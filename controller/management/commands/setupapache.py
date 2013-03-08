from django.conf import settings
from django.core.management.base import BaseCommand

from controller.utils import get_project_root, get_site_root, is_installed
from controller.utils.system import run, check_root
from slices.settings import SLICES_TEMPLATE_IMAGE_DIR, SLICES_SLICE_EXP_DATA_DIR


class Command(BaseCommand):
    help = 'Configures Apache2 to run with your controller instance.'
    
    @check_root
    def handle(self, *args, **options):
        site_root = get_site_root()
        context = { 
            'project_root': get_project_root(),
            'site_root': site_root,
            'media_root': settings.MEDIA_ROOT,
            'static_root': settings.STATIC_ROOT }
        
        apache_conf = (
            'WSGIScriptAlias / %(project_root)s/wsgi.py\n'
            'WSGIPythonPath %(site_root)s/\n\n'
            '<Directory %(project_root)s>/\n'
            '    <Files wsgi.py>\n'
            '        Order deny,allow\n'
            '        Allow from all\n'
            '    </Files>\n'
            '</Directory>\n\n'
            'Alias /media/ %(media_root)s/\n'
            'Alias /static/ %(static_root)s/\n'
            '<Directory %(static_root)s/>\n'
            '    ExpiresActive On\n'
            '    ExpiresByType image/gif A1209600\n'
            '    ExpiresByType image/jpeg A1209600\n'
            '    ExpiresByType image/png A1209600\n'
            '    ExpiresByType text/css A1209600\n'
            '    ExpiresByType text/javascript A1209600\n'
            '    ExpiresByType application/x-javascript A1209600\n'
            '    <FilesMatch "\.(css|js|gz|png|gif|jpe?g|flv|swf|ico|pdf|txt|html|htm)$">\n'
            '        ContentDigest On\n'
            '        FileETag MTime Size\n'
            '    </FilesMatch>\n'
            '</Directory>\n'
            'RedirectMatch ^/$ /admin\n' % context )
        
        if run("grep '^Include httpd.conf' /etc/apache2/apache2.conf", err_codes=[0,1]).return_code == 1:
            run("echo 'Include httpd.conf' >> /etc/apache2/apache2.conf")
        
        diff = run("echo '%s'| diff - /etc/apache2/httpd.conf" % apache_conf, err_codes=[0,1,2])
        if diff.return_code == 2:
            # File does not exist
            run("echo '%s' > /etc/apache2/httpd.conf" % apache_conf)
        elif diff.return_code == 1:
            # File is different, save the old one
            run("cp /etc/apache2/httpd.conf /etc/apache2/httpd.conf.save")
            run("echo '%s' > /etc/apache2/httpd.conf" % apache_conf)    
            print ("\033[1;31mA new version of /etc/apache2/httpd.conf has been installed. "
                   "The old version has been placed at /etc/apache2/httpd.conf.save\033[m")
        
        # run('a2ensite %s' % project_name)
        run('a2enmod expires')
        run('a2enmod deflate')
        
        # Give upload file permissions to apache
        username = run("stat -c %%U %(project_root)s" % context)
        run('adduser www-data %s' % username)
        run('chmod g+w %s' % SLICES_TEMPLATE_IMAGE_DIR)
        run('chmod g+w %s' % SLICES_SLICE_EXP_DATA_DIR)
        if is_installed('firmware'):
            from firmware.settings import FIRMWARE_BASE_IMAGE_PATH
            run('chmod g+w %s' % FIRMWARE_BASE_IMAGE_PATH)
