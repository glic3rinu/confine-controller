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
    Based on OpenWRT ImageBuilder.
    
    Basic usage:
        0. Load the base image
            image = Image('/base/image/file/path.gz')
        1. Initialize workspace.
            image.prepare()
        2. Extract base image.
            image.extract()
        3. Add some files to the base image:
            image.add_file(file)
        4. Generate the new image
            image.build()
        5. Save generated image in a safe place.
            image.move(dest_path)
        6. Clean temporary files created by build() method
            image.clean()
    """
    def __init__(self, base_image):
        os.stat(base_image)
        self.base_image = base_image
        self.files = []
    
    @property
    def mnt(self):
        """ mnt path """
        return os.path.join(self.tmp, 'mnt')
    
    @property
    def scripts(self):
        """ scripts path """
        module_path = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(module_path, 'scripts')
    
    def build(self): #TODO(santiago) allow customization (e.g. PACKAGES)
        """Build the image usin OpenWRT ImageBuilder."""
        packages = "confine-recommended"
        img_builder = os.path.join(self.tmp, 'OpenWrt-ImageBuilder-x86_generic-for-linux-x86_64')
        r('make image -C %s PROFILE="Generic" PACKAGES="%s" FILES="%s"' % (img_builder, packages, self.mnt))
    
    def prepare(self):
        """ create temporary directories needed for building the image """
        self.tmp = tempfile.mkdtemp()
        os.mkdir(self.mnt)
    
    def add_file(self, file):
        """
        add files to the image
        
        file requires a file.name and file.content attributes
        and optionally a file.config.mode with chmod-like syntax.
        """
        self.files.append(file)
    
    def clean(self):
        """Remove temporary files."""
        shutil.rmtree(self.tmp)
    
    def move(self, dst):
        """Move self.file to destination path."""
        shutil.move(self.file, dst)
        self.file = dst
    
    def extract(self):
        """Extract the image."""
        r('tar xjf %s -C %s' % (self.base_image, self.tmp))
        self.builder = os.path.join(self.tmp, os.listdir(self.tmp)[0])
        self.file = os.path.join(self.builder, 'bin/x86/openwrt-x86-generic-combined-ext4.img.gz')
    
    def create_file(self, build_file):
        dest_path = self.mnt + build_file.name
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, mode=0755)
        if os.path.exists(dest_path):
            os.remove(dest_path)
        with open(dest_path, 'w+') as dest_file:
            dest_file.write(build_file.content)
        os.chmod(dest_path, 0644)
        if build_file.config.mode:
            r("chmod %s '%s'" % (build_file.config.mode, dest_path))
