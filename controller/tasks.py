import sys

from celery.task import periodic_task
from celery.task.schedules import crontab
from django.core import management
from django.core.exceptions import ImproperlyConfigured
from StringIO import StringIO

from .settings import CLEAN_ORPHAN_FILES
from .utils.apps import is_installed

@periodic_task(name="controller.delete_orphan_files", run_every=crontab(minute=0, hour=0), enabled=False)
def delete_orphan(*args, **kwargs):
    """
    Delete orphan files like old build firmwares, old base images...
    WARNING: by default this task do nothing and must be configured at
    project settings for a proper functionality defining the setting
    ORPHANED_APPS_MEDIABASE_DIRS, more info at django-orphaned site
    https://github.com/ledil/django-orphaned/
    """
    if not CLEAN_ORPHAN_FILES:
        return "This task is disabled. Check 'CLEAN_ORPHAN_FILES' setting."
    if not is_installed('django_orphaned'):
        raise ImproperlyConfigured("'delete_orphan' task requires django-orphan "\
             "app and is not installed.")

    orig_stdout = sys.stdout
    sys.stdout = content = StringIO()
    
    # Perform a readonly call to get information about deleted files
    management.call_command('deleteorphaned', info=True)
    management.call_command('deleteorphaned')
    
    sys.stdout = orig_stdout
    content.seek(0)
    result = content.getvalue()
    content.close()
    return result.replace('\r', '')

