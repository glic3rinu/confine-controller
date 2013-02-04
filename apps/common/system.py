import subprocess, getpass

from django.core.management.base import CommandError


def check_root(func):
    """ Function decorator that checks if user has root permissions """
    def wrapped(*args, **kwargs):
        if getpass.getuser() != 'root':
            cmd_name = func.__module__.split('.')[-1]
            raise CommandError("Sorry, '%s' must be executed as a superuser (root)" % cmd_name)
        return func(*args, **kwargs)
    return wrapped


class _AttributeString(str):
    """ Simple string subclass to allow arbitrary attribute access. """
    @property
    def stdout(self):
        return str(self)


def run(command, display=True):
    """ Subprocess wrapper for running commands """
    out_stream = subprocess.PIPE
    err_stream = subprocess.PIPE
    
    p = subprocess.Popen(command, shell=True, stdout=out_stream, stderr=err_stream)
    (stdout, stderr) = p.communicate()
    
    out = _AttributeString(stdout.strip())
    err = _AttributeString(stderr.strip())
    
    out.failed = False
    out.return_code = p.returncode
    out.stderr = err
    if p.returncode != 0:
        out.failed = True
        msg = "run() encountered an error (return code %s) while executing '%s'" % (p.returncode, command)
        error(message=msg, stdout=out, stderr=err)
    out.succeeded = not out.failed
    if display:
        print out
    return out


def get_default_celeryd_username():
    """ Introspect celeryd defaults file in order to get default celeryd username """
    user = None
    try:
        celeryd_defaults = open('/etc/default/celeryd')
    except IOError:
        pass
    else:
        for line in celeryd_defaults.readlines():
            if 'CELERYD_USER=' in line:
                user = re.findall('"([^"]*)"', line)[0]
    if user is None:
        raise CommandError("Can not find the default celeryd username")
    return user
