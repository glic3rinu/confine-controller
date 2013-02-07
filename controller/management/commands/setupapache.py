from django.conf import settings
from django.core.management.base import BaseCommand

from controller.utils import get_project_name, get_project_root, get_site_root
from controller.utils.system import run, check_root


class Command(BaseCommand):
    help = 'Configures Apache2 to run with your controller instance.'
    
    @check_root
    def handle(self, *args, **options):
        username = run("ls -dl|awk {'print $3'}")
        project_name = get_project_name()
        project_root = get_project_root()
        site_root = get_site_root()
        apache_conf = (
            'WSGIScriptAlias / %(project_root)s/wsgi.py\n'
            'WSGIPythonPath %(site_root)s\n\n'
            '<Directory %(project_root)s>\n'
            '    <Files wsgi.py>\n'
            '        Order deny,allow\n'
            '        Allow from all\n'
            '    </Files>\n'
            '</Directory>\n\n'
            'Alias /media/ %(site_root)s/media/\n'
            'Alias /static/ %(site_root)s/static/\n'
            '<Directory %(site_root)s/static/>\n'
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
            'RedirectMatch ^/$ /admin\n' % {'project_root': project_root,
                                            'site_root': site_root})
        
        run("echo '%s' > /etc/apache2/httpd.conf" % (apache_conf, project_name))
        run('a2ensite %s.conf' % project_name)
        run('a2enmod expires')
        # Give upload file permissions to apache
        run('adduser www-data %s' % username)
        run('chmod g+w %s/media/firmwares' % site_root)
        run('chmod g+w %s/media/templates' % site_root)
        run('chmod g+w %s/private/exp_data' % site_root)
