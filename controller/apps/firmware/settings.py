from django.conf import settings
from django.core.files.storage import FileSystemStorage

from controller.utils.apps import is_installed


FIRMWARE_BASE_IMAGE_STORAGE = getattr(settings, 'FIRMWARE_BASE_IMAGE_STORAGE', None)


FIRMWARE_BASE_IMAGE_PATH = getattr(settings, 'FIRMWARE_BASE_IMAGE_PATH', 'firmwares')


FIRMWARE_BUILD_IMAGE_STORAGE = getattr(settings, 'FIRMWARE_BUILD_IMAGE_STORAGE',
    FileSystemStorage(location=settings.PRIVATE_MEDIA_ROOT))


FIRMWARE_BUILD_IMAGE_PATH = getattr(settings, 'FIRMWARE_BUILD_IMAGE_PATH', 'firmwares')


FIRMWARE_BASE_IMAGE_EXTENSIONS = getattr(settings, 'FIRMWARE_BASE_IMAGE_EXTENSIONS', ('.img.gz',))


FIRMWARE_PLUGINS_USB_IMAGE = getattr(settings, 'FIRMWARE_PLUGINS_USB_IMAGE',
    '%(site_root)s/confine-install.img.gz')


# FIRMWARE DEFAULT PASSWORD REMOVED
if hasattr(settings, 'FIRMWARE_PLUGINS_PASSWORD_DEFAULT'):
    import warnings
    warnings.warn("FIRMWARE_PLUGINS_PASSWORD_DEFAULT setting has been deprecated "
                  "and is currently unused. You can safely remove it.")


auth_keys_path = ''
if is_installed('maintenance'):
    from maintenance.settings import MAINTENANCE_PUB_KEY_PATH
    auth_keys_path = MAINTENANCE_PUB_KEY_PATH

FIRMWARE_PLUGINS_INITIAL_AUTH_KEYS_PATH = getattr(settings,
    'FIRMWARE_PLUGINS_INITIAL_AUTH_KEYS_PATH', auth_keys_path)
del auth_keys_path
