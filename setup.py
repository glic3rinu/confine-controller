import os
from setuptools import setup, find_packages

packages = find_packages('controller/apps')
#packages.append('static')
packages.append('docs')


setup(
    name = 'confine-controller',
    version = '0.1dev',
    packages = packages,
    package_dir = {
        '' : 'controller/apps',
 #       'static' : 'static',
        'docs' : 'docs',
        'skel' : 'controller/projects/controller',},
    include_package_data = True,
    license = 'BSD License',
    description = 'Django-based framework for building control servers for computer networking and distributed systems testbeds.',
    long_description = 'Django-based framework for building control servers for computer networking and distributed systems testbeds.',
#    install_requires=[
#        'kombu==2.4.7',
#    ],
    scripts=['scripts/controller-admin.sh'],
    url = 'http://wiki.confine-project.eu/soft:server',
    author = 'Marc Aymerich, Santiago Lamora',
    author_email = 'marcay@pangea.org, santiago@pangea.org',
    classifiers = [
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
    ],
)

