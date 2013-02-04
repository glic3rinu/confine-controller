import os

from celery.task import task

from . import settings
from .image import Image


@task(name="firmware.build")
def build(build_id, exclude=[]):
    """ Builds a firmware image for build_obj.node, excluding exclude files """
    # Avoid circular imports
    from .models import Build, Config
    
    # retrieve the existing build instance, used for user feedback
    build_obj = Build.objects.get(pk=build_id)
    build_obj.task_id = build.request.id
    build_obj.save()
    
    config = Config.objects.get()
    node = build_obj.node
    base_image = config.get_image(node)
    
    # prepare the image adding the files
    image = Image(base_image.path)
    for build_file in config.eval_files(node, exclude=exclude, image=image):
        image.add_file(build_file)
        build_file.build = build_obj
        build_file.save()
    
    # image destination path
    name_dict = {
        'node_name': node.name,
        'arch': node.arch,
        'build_id': build_obj.pk,
        'version': config.version}
    image_name = os.path.join(settings.FIRMWARE_DIR, config.image_name % name_dict)
    image_path = os.path.join(build_obj.image.storage.location, image_name)
    
    try:
        image.build(path=image_path)
    except:
        image.clean()
        raise
    
    image.clean()
    build_obj.image = image_name
    build_obj.save()
    
    return image_path
