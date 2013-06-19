import itertools, os

from django.core.files.storage import FileSystemStorage


from controller.settings import DOUBLE_EXTENSIONS


class DoubleExtensionAwareFileSystemStorage(FileSystemStorage):
    def get_available_name(self, name):
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        dir_name, file_name = os.path.split(name)
        file_root, file_ext = os.path.splitext(file_name)
        
        if any([file_name.endswith(x) for x in DOUBLE_EXTENSIONS]):
            file_root, first_ext = os.path.splitext(file_root)
            file_ext = first_ext + file_ext
        
        # If the filename already exists, add an underscore and a number (before
        # the file extension, if one exists) to the filename until the generated
        # filename doesn't exist.
        count = itertools.count(1)
        while self.exists(name):
            name = os.path.join(dir_name, "%s_%s%s" % (file_root, next(count), file_ext))
        
        return name

