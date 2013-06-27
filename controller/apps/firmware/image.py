import functools
import os
import shutil
import tempfile

from controller.utils.system import run


r = functools.partial(run, silent=False)

# TODO rename self.image to self.file or something  path ? !

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
            context = { 'image': self.image, 'part_nr': self.part_nr }
            #BUGFIX: file -k option for keep looking and getting all file image info
            # different output at UNIX `file` between version 5.11 and 5.14
            result = r("file -k %(image)s|grep -Po '(?<=startsector ).*?(?=,)'|"
                       "sed -n %(part_nr)dp" % context)
            try:
                self._sector = int(result.stdout)
            except ValueError:
                # TODO custom exception
                raise Exception("Failed getting image start sector (value '%s'). "
                    "Has selected base image a valid image file?" % result.stdout)
        return self._sector
    
    @property
    def mount_context(self):
        """ context used in mount and umount methods """
        return { 'mnt': self.mnt,
                 'image': self.image,
                 'partition': self.partition,
                 'sector': self.sector }
    
    def prepare(self):
        """ create temporary directories needed for building the image """
        self.tmp = tempfile.mkdtemp()
        os.mkdir(self.mnt)
        self.image = os.path.join(self.tmp, "image.bin")
    
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
    
    def umount(self, quiet=False):
        """ umount image partition """
        context = self.mount_context
        err_codes = [0, 1] if quiet else [0]
        r("fusermount -u %(mnt)s" % context, err_codes=err_codes)
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
            self.umount(quiet=True) # silent error entry not found in /etc/mtab
        finally:
            shutil.rmtree(self.tmp)
    
    def move(self, dst):
        """ move self.image to destination path """
        shutil.move(self.image, dst)
        self.image = dst
    
    def gunzip(self):
        """ extract the image """
        r("cat '%s' | gunzip -c > '%s'" % (self.base_image, self.image))
    
    def gzip(self):
        """ compress the image """
        r("gzip " + self.image)
        self.image += '.gz'
    
    def create_file(self, build_file):
        dest_path = self.mnt + build_file.name
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        if os.path.exists(dest_path):
            os.remove(dest_path)
        with open(dest_path, 'w+') as dest_file:
            dest_file.write(build_file.content)
        if build_file.config.mode:
            r("chmod %s '%s'" % (build_file.config.mode, dest_path))
