import gzip, os, tempfile, shutil
from subprocess import Popen, PIPE


class Image(object):
    def __init__(self, base_image):
        os.stat(base_image)
        self.base_image = base_image
        self.tmp = tempfile.mkdtemp()
        self.image = os.path.join(self.tmp, "image.bin")
        self.mnt = os.path.join(self.tmp, "mnt")
        self.base_dir = os.path.dirname(os.path.realpath(__file__))
        self.tmp_part_file = os.path.join(self.tmp, 'part.img')
        self.files = []
        os.mkdir(self.mnt)
    
    def mount(self, part_nr=2):
        args = "'%s' %s %s %s" % (self.image, self.mnt, self.tmp_part_file, part_nr)
        mountimage = "%s/scripts/mountimage.sh -m %s" % (self.base_dir, args)
        self._exec_cmd(mountimage)
    
    def umount(self, part_nr=2):
        args = "'%s' %s %s %s" % (self.image, self.mnt, self.tmp_part_file, part_nr)
        umountimage = "%s/scripts/mountimage.sh -u %s" % (self.base_dir, args)
        self._exec_cmd(umountimage)
    
    def add_file(self, file):
        self.files.append(file)
    
    def clean(self):
        try: self.umount()
        except: pass
        shutil.rmtree(self.tmp)
    
    def move(self, path):
        shutil.move(self.image, path)
    
    def chmod(self, path, mode):
        chmod = "chmod %s '%s'" % (mode, path) 
        self._exec_cmd(chmod)
    
    def build(self, path=None):
        extract = "cat '%s' | gunzip -c > '%s'" %(self.base_image, self.image)
        self._exec_cmd(extract)
        self.mount()
        
        # add files to base_image
        for f in self.files:
            dest_path = self.mnt + f.path
            dest_dir = os.path.dirname(dest_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            if os.path.exists(dest_path):
                os.remove(dest_path)
            dest_file = open(dest_path, 'w+')
            dest_file.write(f.value)
            dest_file.close()
            if f.mode:
                self.chmod(dest_path, f.mode)
        
        self.umount()
        compress = "gzip " + self.image
        self._exec_cmd(compress)
        self.image += '.gz'
        
        if path is not None:
            self.move(path)
    
    def _exec_cmd(self, command, part_nr=2):
        mount_errors = {
            11: "Unable to find start sector for part %s" % part_nr,
            12: "%s already mounted" % self.mnt,
            13: "Error extracting part %s" % part_nr,
            14: "Cannot mount extracted part %s" % part_nr,
            15: "Unable to unmount %s" % self.mnt,
            16: "Error joining extracted part %s" % part_nr}
        
        cmd = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        (stdout, stderr) = cmd.communicate()
        returncode = cmd.returncode
        if returncode > 0:
            error_msg = ""
            try: error_msg += "%s --  " % mount_errors[returncode]
            except KeyError: pass
            error_msg += stderr
            raise self.BuildError(error_msg)
    
    class BuildError(Exception): pass



