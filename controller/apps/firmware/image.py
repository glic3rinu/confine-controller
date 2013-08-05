import functools
import os
import shutil
import tempfile

from django.core.management.base import CommandError

from controller.utils.system import run, makedirs

from .exceptions import UnexpectedImageFormat


r = functools.partial(run, silent=False)


class Image(object):
    """ 
    Class-based firmware customization.
    Based on user-space tools, with partition support.
    
    Basic usage:
        1. Load the base image
            image = Image('/base/image/file/path.gz')
        2. Add some files to the base image:
            image.add_file(file)
        3. Generate the new image
            image.build(path='/destination/image/path.gz')
        4. Clean temporary files created by build() method
            image.clean()
    """
    def __init__(self, base_image, part_nr=2):
        os.stat(base_image)
        self.base_image = base_image
        self.files = []
        self.part_nr = part_nr
    
    @property
    def mnt(self):
        """ mnt path """
        return os.path.join(self.tmp, 'mnt')
    
    @property
    def partition(self):
        """ partition path """
        return os.path.join(self.tmp, 'part.img')
    
    @property
    def scripts(self):
        """ scripts path """
        module_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(module_path, 'scripts')
    
    @property
    def sector(self):
        """ sector number of image part_nr """
        if not hasattr(self, '_sector'):
            context = { 'image': self.file, 'part_nr': self.part_nr }
            # File -k option for keep looking and getting part_nr sector number
            # different behaviour between version 5.11 and 5.14
            result = r("file -k %(image)s|grep -Po '(?<=startsector ).*?(?=,)'|"
                       "sed -n %(part_nr)dp" % context)
            try:
                self._sector = int(result.stdout)
            except ValueError:
                msg = '"%s" is not a valid sector number' % result.stdout
                raise UnexpectedImageFormat(msg)
        return self._sector
    
    @property
    def mount_context(self):
        """ context used in mount and umount methods """
        return { 'mnt': self.mnt,
                 'image': self.file,
                 'partition': self.partition,
                 'sector': self.sector }
    
    def prepare(self):
        """ create temporary directories needed for building the image """
        self.tmp = tempfile.mkdtemp()
        os.mkdir(self.mnt)
        self.file = os.path.join(self.tmp, "image.bin")
    
    def mount(self):
        """ mount image partition with user-space tools """
        context = self.mount_context
        # raise an exception if there is something mounted on our target
        r("mountpoint -q %(mnt)s" % context, err_codes=[1])
        r("dd if=%(image)s of=%(partition)s skip=%(sector)d" % context)
        r("fuseext2 %(partition)s %(mnt)s -o rw+" % context)
        # fuseext2 is a pice of crap since doesn't return a correct exit code
        # raising an exception if fuseext2 didn't succeed
        r("mountpoint -q %(mnt)s" % context)
    
    def umount(self):
        """ umount image partition """
        context = self.mount_context
        # raise an exception if there is nothing mounted in our target
        r("fusermount -u %(mnt)s" % context)
        r("dd if=%(partition)s of=%(image)s seek=%(sector)d" % context)
    
    def add_file(self, file):
        """
        add files to the image
        
        file requires a file.name and file.content attributes
        and optionally a file.config.mode with chmod-like syntax.
        """
        self.files.append(file)
    
    def clean(self):
        """ remove temporary files """
        try:
            self.umount()
        except CommandError:
            # umount may fail because the image is already umounted
            pass
        finally:
            shutil.rmtree(self.tmp)
    
    def move(self, dst):
        """ move self.file to destination path """
        shutil.move(self.file, dst)
        self.file = dst
    
    def gunzip(self):
        """ extract the image """
        r("cat '%s' | gunzip -c > '%s'" % (self.base_image, self.file))
    
    def gzip(self):
        """ compress the image file """
        r("gzip " + self.file)
        self.file += '.gz'
    
    def create_file(self, build_file):
        dest_path = self.mnt + build_file.name
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            makedirs(dest_dir, mode=0755, uid=0, gid=0)
        if os.path.exists(dest_path):
            os.remove(dest_path)
        with open(dest_path, 'w+') as dest_file:
            dest_file.write(build_file.content)
        os.chown(dest_path, 0, 0)
        os.chmod(dest_path, 0644)
        if build_file.config.mode:
            r("chmod %s '%s'" % (build_file.config.mode, dest_path))
