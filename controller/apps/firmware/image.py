import gzip, os, tempfile, shutil
from subprocess import Popen, PIPE


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
        mountimage = "%s/mountimage.sh -m %s" % (self.scripts, args)
        self._exec_cmd(mountimage)
    
    def umount(self):
        """ umount image partition """
        args = "'%s' %s %s %s" % (self.image, self.mnt, self.partition, self.part_nr)
        umountimage = "%s/mountimage.sh -u %s" % (self.scripts, args)
        self._exec_cmd(umountimage)
    
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
        chmod = "chmod %s '%s'" % (mode, path) 
        self._exec_cmd(chmod)
    
    def build(self, path=None):
        """ build the new image """
        # create temporary dirs
        self.prepare()
        # extract the image
        extract = "cat '%s' | gunzip -c > '%s'" %(self.base_image, self.image)
        self._exec_cmd(extract)
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
        compress = "gzip " + self.image
        self._exec_cmd(compress)
        self.image += '.gz'
        
        # move the image to the destination path if required
        if path is not None:
            self.move(path)
    
    def _exec_cmd(self, command):
        """ Execute shell commands """
        mount_errors = {
            11: "Unable to find partition start sector",
            12: "%s already mounted" % self.mnt,
            13: "Error extracting partition",
            14: "Cannot mount extracted partition",
            15: "Unable to unmount %s" % self.mnt,
            16: "Error joining extracted partition"}
        
        cmd = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = cmd.communicate()
        returncode = cmd.returncode
        if returncode > 0:
            error_msg = ""
            try:
                error_msg += "%s --  " % mount_errors[returncode]
            except KeyError:
                pass
            error_msg += stderr
            raise self.BuildError(error_msg)
    
    class BuildError(Exception): pass

