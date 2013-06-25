import os

from django.conf import settings
from django.core.files.storage import FileSystemStorage


FIRMWARE_BASE_IMAGE_STORAGE = getattr(settings, 'FIRMWARE_BASE_IMAGE_STORAGE', None)

FIRMWARE_BASE_IMAGE_PATH = getattr(settings, 'FIRMWARE_BASE_IMAGE_PATH', 'firmwares')

FIRMWARE_BASE_IMAGE_EXT = getattr(settings, 'FIRMWARE_BASE_IMAGE_EXT', '.img.gz')

FIRMWARE_BUILD_IMAGE_STORAGE = getattr(settings, 'FIRMWARE_BUILD_IMAGE_STORAGE',
    FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT))

FIRMWARE_BUILD_IMAGE_PATH = getattr(settings, 'FIRMWARE_BUILD_IMAGE_PATH', 'firmwares')

FIRMWARE_PLUGINS_USB_IMAGE = getattr(settings, 'FIRMWARE_PLUGINS_USB_IMAGE',
    '%(site_root)s/confine-install.img.gz')
