import os

from celery.task import task
from django.core.exceptions import ImproperlyConfigured

from .image import Image


def update_state(build, progress, next, description):
    build.update_state(state='PROGRESS',
        meta={'progress': progress, 'next': next, 'description': description})


@task(name="firmware.build")
def build(build_id, exclude=[]):
    """ Builds a firmware image for build.node, excluding exclude files """
    # Avoid circular imports
    from .models import Build, Config
    
    # retrieve the existing build instance, used for user feedback
    update_state(build, 1, 4, 'Build started')
    build_obj = Build.objects.get(pk=build_id)
    build_obj.task_id = build.request.id
    build_obj.save()
    
    config = Config.objects.get()
    node = build_obj.node
    base_image = config.get_image(node)
    if base_image is None: # this should be avoided before running this task
        raise ImproperlyConfigured("Error building the firmware. Does not \
            exists a base image for %s arch (node %s)" % (node.arch, node.id))
    image = Image(base_image.path)
    
    try:
        # Build the image
        image.prepare()
        
        update_state(build, 5, 14, 'Unpackaging base image')
        image.gunzip()
        
        update_state(build, 15, 29, 'Preparing image file system')
        image.mount()

        files = config.eval_files(node, exclude=exclude, image=image)
        total = len(files)
        for num, build_file in enumerate(files):
            current = 30 + num/total*25
            next = min(30 + (num+1)/total*25, 59)
            update_state(build, current, next, 'Generating %s file' % build_file.name)
            image.create_file(build_file)
            build_file.build = build_obj
            build_file.save()
        
        update_state(build, 60, 74, 'Unmounting image file system')
        image.umount()
        
        update_state(build, 75, 94, 'Compressing image')
        image.gzip()
        
        update_state(build, 95, 99, 'Cleaning up')
        dest_path = config.get_dest_path(node, build=build_obj)
        image.move(dest_path)
    finally:
        image.clean()
    
    build_obj.image = dest_path
    build_obj.base_image = base_image
    build_obj.save()
    return { 'progress': 99, 'description': 'Redirecting', 'result': dest_path }
