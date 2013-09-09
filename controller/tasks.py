import sys

from celery.task import periodic_task
from celery.task.schedules import crontab
from django.core import management
from StringIO import StringIO

@periodic_task(name="controller.delete_orphan_files", run_every=crontab(minute=0, hour=0))
def delete_orphan(*args, **kwargs):
    """
    Delete orphan files like old build firmwares, old base images...
    WARNING: by default this task do nothing and must be configured at
    project settings for a proper functionality defining the setting
    ORPHANED_APPS_MEDIABASE_DIRS, more info at django-orphaned site
    https://github.com/ledil/django-orphaned/
    """
    orig_stdout = sys.stdout
    sys.stdout = content = StringIO()

    management.call_command('deleteorphaned')

    sys.stdout = orig_stdout
    content.seek(0)
    result = content.getvalue()
    content.close()
    return result.replace('\r', '').replace('\n', '')

