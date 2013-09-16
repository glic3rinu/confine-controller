from .image import Image
from .models import Config


def debug_build(node, base_image=None, exclude=[]):
    """ 
    Function used for debuging the firmware generation
        from firmware.debug import debug_build
        from nodes.models import Node
        debug_build(Node.objects.all()[0])
    """
    config = Config.objects.get()
    if base_image is None:
        base_image = config.get_image(node)
    else:
        base_image = base_image.image
    image = Image(base_image.path)
    
    try:
        # Build the image
        image.prepare()
        image.gunzip()
        image.mount()
        files = config.eval_files(node, exclude=exclude, image=image)
        for num, build_file in enumerate(files):
            if num not in ['9', '10', '3']:
                image.create_file(build_file)
        image.umount()
        image.gzip()
        
        dest_path = config.get_dest_path(node)
        image.move(dest_path)
    finally:
        image.clean()
    
    print 'Success %s' % dest_path

