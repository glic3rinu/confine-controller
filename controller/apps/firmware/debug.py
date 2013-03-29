from firmware.image import Image
from firmware.models import Config


def debug_build(node, exclude=[]):
    """ 
    Function used for debuging the firmware generation
        from firmware.debug import debug_build
        from nodes.models import Node
        debug_build(Node.objects.all()[0])
    """
    config = Config.objects.get()
    base_image = config.get_image(node)
    image = Image(base_image.image.path)
    
    try:
        # Build the image
        image.prepare()
        image.gunzip()
        image.mount()
        files = config.eval_files(node, exclude=exclude, image=image)
        for num, build_file in enumerate(files):
            image.create_file(build_file)
        image.umount()
        image.gzip()
        
        dest_path = config.get_dest_path(node)
        image.move(dest_path)
    finally:
        image.clean()
    
    print 'Success %s' % dest_path

