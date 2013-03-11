import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


ugettext = lambda s: s


FIRMWARE_BASE_IMAGE_STORAGE = getattr(settings, 'FIRMWARE_BASE_IMAGE_STORAGE', None)

FIRMWARE_BASE_IMAGE_PATH = getattr(settings, 'FIRMWARE_BASE_IMAGE_PATH', 'firmwares')


FIRMWARE_BUILD_IMAGE_STORAGE = getattr(settings, 'FIRMWARE_BUILD_IMAGE_STORAGE',
    FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT))

FIRMWARE_BUILD_IMAGE_PATH = getattr(settings, 'FIRMWARE_BUILD_IMAGE_PATH', 'firmwares')
