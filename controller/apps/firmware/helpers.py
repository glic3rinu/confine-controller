import os.path

from django.conf import settings as controller_settings

from . import settings


def filename_handler(instance, filename):
    """ Handle filename for renaming if the file alreday exists. """
    path = os.path.join(controller_settings.MEDIA_ROOT, 
                        settings.FIRMWARE_BASE_IMAGE_PATH)
    file_ext = settings.FIRMWARE_BASE_IMAGE_EXT 

    i = 1
    name = filename.rstrip(file_ext)
    while True: # generate filename until file not exists
        abs_path = os.path.join(path, filename)
        if not os.path.exists(abs_path):
            break
        filename = "%s_%s%s" % (name, i, file_ext)
        i += 1
    
    return os.path.join(settings.FIRMWARE_BASE_IMAGE_PATH, filename)
