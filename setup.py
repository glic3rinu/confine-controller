import os
from setuptools import setup


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('controller'):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.') or dirname == '__pycache__':
            del dirnames[i]
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])


setup(
    name = 'confine-controller',
    version = '0.1dev',
    packages = packages,
#    package_data={
#        'controller': ['templates/tastypie/*'],
#    },

    include_package_data = True,
    license = 'BSD License',
    description = 'Django-based framework for building control servers for computer networking and distributed systems testbeds.',
    long_description = 'Django-based framework for building control servers for computer networking and distributed systems testbeds.',
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

