import os

from celery.task import task

from .images import Image

@task(name="firmware.build")
def build(build_id, options={}):
    from firmware.models import Build, Config
    
    # retrieve the existing build instance, used for user feedback
    build_obj = Build.objects.get(pk=build_id)
    build_obj.task_id = build.request.id
    build_obj.save()
    
    config = Config.objects.get()
    node = build_obj.node
    base_image = config.get_image(node)
    
    # prepare the new image and copy the files in it
    image = Image(base_image.path)

    for f in config.get_files(node):
        image.add_file(f)
    
    # calculating image destination path
    image_name = base_image.name.replace('.gz', '-%s.gz' % build_obj.pk)
    image_path = os.path.join(build_obj.image.storage.location, image_name)
    
    # build the image
    try: 
        image.build(path=image_path)
    except: 
        image.clean()
        raise
    
    image.clean()
    build_obj.image = image_name
    build_obj.save()
    
    return image_path
