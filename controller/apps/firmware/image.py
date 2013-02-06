import gzip, os, tempfile, shutil
from subprocess import Popen, PIPE

from common.system import run


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
    
    def prepare(self):
        """ create temporary directories needed for building the image """
        self.tmp = tempfile.mkdtemp()
        os.mkdir(self.mnt)
        self.image = os.path.join(self.tmp, "image.bin")
    
    def mount(self):
        """ mount image partition with user-space tools """
        args = "'%s' %s %s %s" % (self.image, self.mnt, self.partition, self.part_nr)
        script = os.path.join(self.scripts, "mountimage.sh")
        # TODO This is a workaround for this issue https://github.com/pypa/pip/issues/317
        run("chmod +x %s" % script)
        run("%s -m %s" % (script, args), silent=False)
    
    def umount(self):
        """ umount image partition """
        args = "'%s' %s %s %s" % (self.image, self.mnt, self.partition, self.part_nr)
        run("%s/mountimage.sh -u %s" % (self.scripts, args), silent=False)
    
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
        except:
            pass
        shutil.rmtree(self.tmp)
    
    def move(self, dst):
        """ move self.image to destination path """
        shutil.move(self.image, dst)
        self.image = dst
    
    def chmod(self, path, mode):
        """ change mode of the path """
        run("chmod %s '%s'" % (mode, path), silent=False)
    
    def build(self, path=None):
        """ build the new image """
        # create temporary dirs
        self.prepare()
        # extract the image
        run("cat '%s' | gunzip -c > '%s'" %(self.base_image, self.image), silent=False)
        self.mount()
        
        # create the added files
        for f in self.files:
            dest_path = self.mnt + f.name
            dest_dir = os.path.dirname(dest_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            if os.path.exists(dest_path):
                os.remove(dest_path)
            dest_file = open(dest_path, 'w+')
            dest_file.write(f.content)
            dest_file.close()
            if f.config.mode:
                self.chmod(dest_path, f.config.mode)
        
        self.umount()
        # compress the generated image with gzip
        run("gzip " + self.image, silent=False)
        self.image += '.gz'
        
        # move the image to the destination path if required
        if path is not None:
            self.move(path)
