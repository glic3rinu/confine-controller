from datetime import timedelta

from django.conf import settings


MONITOR_ALERT_EXPIRATION = getattr(settings, 'MONITOR_ALERT_EXPIRATION', timedelta(days=1))

MONITOR_ALERT_LOCK = getattr(settings, 'MONITOR_ALERT_LOCK', '/dev/shm/.controller.monitor.lock')

MONITOR_EXPIRE_SECONDS = getattr(settings, 'MONITOR_EXPIRE_SECONDS', 300)

# ~1GB (rabbitmq default disk free limit)
MONITOR_DISK_FREE_LIMIT = getattr(settings, 'MONITOR_DISK_FREE_LIMIT', 1000000)

# warn margin ratio (allow admins prevent problem)
MONITOR_DISK_WARN_RATIO = getattr(settings, 'MONITOR_DISK_WARN_RATIO', 1.2)

# name, ps cmd regex, min, max
TINC = ('tinc', '.*tincd', 1, 1)
# By default celery_w1 has 5 processes + 1 coordinator = 6
CELERY_W1 = ('celery_w1', '.*python.*celery.*-n w1\.', 6, None)
CELERY_W2 = ('celery_w2', '.*python.*celery.*-n w2\.', 1, 1)
CELERYEV = ('celeryev', '.*python .*celeryev', 1, 1)
CELERYBEAT = ('celerybeat', '.*python .*celerybeat', 1, 1)
APACHE2 = ('apache2', '.*apache2', 3, None)
WSGI = ('wsgi', '\(wsgi', 2, None)
NGINX = ('nginx', '\n.*nginx', 3, None)
UWSGI = ('uwsgi', '\n.*uwsgi', 8, None)
POSTGRESQL = ('postgresql', '.*postgres', 1, None)
RABBITMQ = ('rabbitmq', '[./]*rabbit', 2, 2)


MONITOR_MONITORS = getattr(settings, 'MONITOR_MONITORS', (
    ('monitor.monitors.NumProcessesMonitor', {
            'processes': (TINC, CELERY_W1, CELERY_W2, CELERYEV, CELERYBEAT,
                          POSTGRESQL, RABBITMQ)
        }),
    ('monitor.monitors.LoadAvgMonitor',),
    ('monitor.monitors.FreeMonitor',),
#    ('monitor.monitors.Apache2StatusMonitor', {
#            'url': 'http://localhost/server-status',
#        }),
#    ('monitor.monitors.NginxStatusMonitor', {
#            'url': 'https://controller.confine-project.eu/status',
#        }),
#    ('monitor.monitors.DebugPageLoadTimeMonitor', {
#            'name': 'indexpageload',
#            'url': 'http://127.0.0.1/admin/'
#        }),
#    ('monitor.monitors.DebugPageLoadTimeMonitor', {
#            'name': 'apiuserpageload',
#            'url': 'http://127.0.0.1/api/nodes/'
#        }),
#    ('monitor.monitors.BasicNetMonitor', {'iface': 'confine'}),
    ('monitor.monitors.ProcessesCPUMonitor', {
            'processes': (TINC, CELERY_W1, CELERY_W2, POSTGRESQL, RABBITMQ),
        }),
    ('monitor.monitors.ProcessesMemoryMonitor', {
            'processes': (TINC, CELERY_W1, CELERY_W2, POSTGRESQL),
        }),
    ('monitor.monitors.DiskFreeMonitor',),
))
