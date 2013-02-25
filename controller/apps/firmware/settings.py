import os

from django.conf import settings


ugettext = lambda s: s


FIRMWARE_BASE_IMAGE_PATH = getattr(settings, 'FIRMWARE_BASE_IMAGE_PATH',
    os.path.join(settings.MEDIA_ROOT, 'firmwares'))

FIRMWARE_BUILD_PATH = getattr(settings, 'FIRMWARE_BUILD_PATH',
    os.path.join(settings.PRIVATE_MEDIA_ROOT, 'firmwares'))


