import os, sys
from distutils.sysconfig import get_python_lib
from setuptools import setup, find_packages


# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent Controller are
# still present in site-packages.
overlay_warning = False
if "install" in sys.argv:
    # We have to try also with an explicit prefix of /usr/local in order to
    # catch Debian's custom user site-packages directory.
    for lib_path in get_python_lib(), get_python_lib(prefix="/usr/local"):
        existing_path = os.path.abspath(os.path.join(lib_path, "controller"))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

packages = find_packages('.')

# Dynamically calculate the version based on controller.VERSION.
version = __import__('controller').get_version()

setup(
    name = 'confine-controller',
    version = version,
    packages = packages,
    include_package_data = True,
    license = 'BSD License',
    description = ('Django-based framework for building control servers for computer '
                   'networking and distributed systems testbeds.'),
    scripts=['controller/bin/controller-admin.sh'],
    url = 'http://wiki.confine-project.eu/soft:server',
    author = 'CONFINE Project',
    author_email = 'support@confine-project.eu',
#    install_requires=[
#        'paramiko',
#    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)


if overlay_warning:
    sys.stderr.write("""

========
WARNING!
========

You have just installed confine-controller over top of an existing 
installation, without removing it first. 
Because of this, your install may now include extraneous 
files from a previous version that have since been removed from
Controller. This is known to cause a variety of problems. You
should manually remove the

%(existing_path)s

directory and re-install confine-controller.


You don't have to worry if you're upgrading using the standard procedure:

python manage.py upgradecontroller

""" % { "existing_path": existing_path })

