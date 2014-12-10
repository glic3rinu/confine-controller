from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.six.moves import input

from controller.utils.paths import get_project_root, get_site_root, get_project_name
from controller.utils.system import run, check_root, get_default_celeryd_username

from pki import ca


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--user', dest='user', default=get_default_celeryd_username(),
                help='WSGIDaemonProcess user.'),
            make_option('--group', dest='group', default='',
                help='WSGIDaemonProcess group.'),
            make_option('--processes', dest='processes', default=4,
                help='WSGIDaemonProcess processes.'),
            make_option('--threads', dest='threads', default=50,
                help='WSGIDaemonProcess threads.'),
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help='Tells Django to NOT prompt the user for input of any kind.'),
            )
    
    option_list = BaseCommand.option_list
    help = 'Configures Apache2 to run with your controller instance.'
    
    @check_root
    def handle(self, *args, **options):
        interactive = options.get('interactive')
        
        # Avoid import errors
        from nodes.models import Server
        server = Server.objects.first()
        context = {
            'project_name': get_project_name(),
            'project_root': get_project_root(),
            'site_root': get_site_root(),
            # TODO end with single /
            'media_root': settings.MEDIA_ROOT,
            'static_root': settings.STATIC_ROOT,
            'cert_path': ca.cert_path,
            'cert_key_path': ca.priv_key_path,
            'mgmt_addr': str(server.mgmt_net.addr),
            'user': options.get('user'),
            'group': options.get('group') or options.get('user'),
            'processes': int(options.get('processes')),
            'threads': int(options.get('threads')) }
        
        apache_conf = (
            'WSGIDaemonProcess %(project_name)s user=%(user)s group=%(group)s processes=%(processes)d \\\n'
            '                  threads=%(threads)d python-path=%(site_root)s \\\n'
            '                  display-name=%%{GROUP}\n'
            'WSGIProcessGroup %(project_name)s\n'
            'WSGIScriptAlias / %(project_root)s/wsgi.py\n'
            'WSGIPassAuthorization On\n\n'
            '<Directory %(project_root)s>\n'
            '    <Files wsgi.py>\n'
            '        Order deny,allow\n'
            '        Allow from all\n'
            '    </Files>\n'
            '</Directory>\n\n'
            'Alias /media/ %(media_root)s/\n'
            'Alias /static/ %(static_root)s/\n'
            '<Directory %(static_root)s>\n'
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
            '</Directory>\n\n'
            'RedirectMatch ^/$ /admin\n\n'
            '<VirtualHost [%(mgmt_addr)s]:443>\n'
            '    ServerName localhost\n'
            '    SSLEngine on\n'
            '    SSLCertificateFile %(cert_path)s\n'
            '    SSLCertificateKeyFile %(cert_key_path)s\n'
            '    SSLCACertificateFile %(cert_path)s\n'
            '    SSLVerifyClient None\n'
            '</VirtualHost>' % context)
        
        context.update({
            'apache_conf': apache_conf,
            'apache_conf_file': '/etc/apache2/conf.d/%(project_name)s.conf' % context})
        
        diff = run("echo '%(apache_conf)s'|diff - %(apache_conf_file)s" % context, err_codes=[0,1,2])
        if diff.return_code == 2:
            # File does not exist
            run("echo '%(apache_conf)s' > %(apache_conf_file)s" % context)
        elif diff.return_code == 1:
            # File is different, save the old one
            if interactive:
                msg = ("\n\nFile %(apache_conf_file)s should be updated, do "
                       "you like to override it? (yes/no): " % context)
                confirm = input(msg)
                while 1:
                    if confirm not in ('yes', 'no'):
                        confirm = input('Please enter either "yes" or "no": ')
                        continue
                    if confirm == 'no':
                        return
                    break
            run("cp %(apache_conf_file)s %(apache_conf_file)s.\$save" % context)
            run("echo '%(apache_conf)s' > %(apache_conf_file)s" % context)
            self.stdout.write("\033[1;31mA new version of %(apache_conf_file)s "
                "has been installed.\n The old version has been placed at "
                "%(apache_conf_file)s.$save\033[m" % context)
        
#        include_httpd = run("grep '^\s*Include\s\s*httpd.conf\s*' /etc/apache2/apache2.conf", err_codes=[0,1])
#        if include_httpd.return_code == 1:
#            run("echo 'Include httpd.conf' >> /etc/apache2/apache2.conf")
        
        # run('a2ensite %s' % project_name)
        run('a2enmod wsgi')
        run('a2enmod expires')
        run('a2enmod deflate')
        run('a2enmod ssl')
        
        # Give upload file permissions to apache
#        username = run("stat -c %%U %(project_root)s" % context)
#        run('adduser www-data %s' % username)
#        run('chmod g+w %(media_root)s' % context)
        
        # Give read permissions to cert key file
        run('chmod g+r %(cert_key_path)s' % context)
