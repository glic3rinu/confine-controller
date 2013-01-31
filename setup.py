import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


packages = find_packages('controller/apps')
packages.append('static')
packages.append('docs')


setup(
    name = 'confine-controller',
    version = '0.1dev',
    packages = packages,
    include_package_data = True,
    license = 'BSD License',
    description = 'Django-based framework for building control servers for computer networking and distributed systems testbeds.',
    long_description = README.md,
    install_requires=[
        'django==1.5',
        'django-fluent-dashboard',
        'south',
        'markdown',
        'django-private-files',
        'IPy',
        'git+https://github.com/alex/django-filter.git#egg=django-filter',
        'django-singletons',
        'django-extensions',
        'django_transaction_signals',
        'django-celery',
        'kombu==2.4.7',
        'django-celery-email',
    ],
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

