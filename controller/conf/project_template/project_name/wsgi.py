"""
WSGI config for {{ project_name }} project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/{{ docs_version }}/howto/deployment/wsgi/
"""

import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ project_name }}.settings")
sys.path.append('{{ project_directory }}')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

