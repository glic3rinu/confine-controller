from django.conf import settings


MONITOR_EXPIRE_SECONDS = getattr(settings, 'MONITOR_EXPIRE_SECONDS', 300)


# name, ps cmd regex, min, max
TINC = ('tinc', '.*tincd', 1, 1)
CELERY_W1 = ('celery_w1', '.*python.*celery.*-n w1\.', 8, None)
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
    ('monitor.monitors.NumPocessesMonitor', {
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
))