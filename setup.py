import os
from setuptools import setup, find_packages

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

packages = find_packages('.')

setup(
    name = 'confine-controller',
    version = '0.6.9dev',
    packages = packages,
    include_package_data = True,
    license = 'BSD License',
    description = 'Django-based framework for building control servers for computer networking and distributed systems testbeds.',
    scripts=['controller/bin/controller-admin.sh'],
    url = 'http://wiki.confine-project.eu/soft:server',
    author = 'Confine Project',
    author_email = 'support@confine-project.eu',
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

