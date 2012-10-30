from django.conf import settings

ugettext = lambda s: s


FIRMWARE_DIR = getattr(settings, 'FIRMWARE_DIR', 'firmwares/')



