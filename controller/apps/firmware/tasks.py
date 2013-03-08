import os

from celery.task import task

from .image import Image


def update_state(build, progress, description):
    build.update_state(state='PROGRESS',
        meta={'progress': progress, 'description': description})


@task(name="firmware.build")
def build(build_id, exclude=[]):
    """ Builds a firmware image for build.node, excluding exclude files """
    # Avoid circular imports
    from .models import Build, Config
    
    # retrieve the existing build instance, used for user feedback
    update_state(build, 1, 'Build started')
    build_obj = Build.objects.get(pk=build_id)
    build_obj.task_id = build.request.id
    build_obj.save()
    
    config = Config.objects.get()
    node = build_obj.node
    base_image = config.get_image(node)
    
    try:
        # Build the image
        image = Image(base_image.image.path)
        image.prepare()
        
        update_state(build, 5, 'Unpackaging base image')
        image.gunzip()
        
        update_state(build, 10, 'Preparing image file system')
        image.mount()
        
        files = config.eval_files(node, exclude=exclude, image=image)
        total = len(files)
        for num, build_file in enumerate(files):
            update_state(build, 10 + num/total*30, 'Generating %s file' % build_file.name)
            image.create_file(build_file)
            build_file.build = build_obj
            build_file.save()
        
        update_state(build, 50, 'Unmounting image file system')
        image.umount()
        
        update_state(build, 60, 'Compressing image')
        image.gzip()
        
        update_state(build, 90, 'Cleaning up')
        dest_path = build_obj.get_dest_path()
        image.move(dest_path)
    finally:
        image.clean()
    
    build_obj.image = build_obj.get_image_name()
    build_obj.base_image = base_image
    build_obj.save()
    
    return { 'progress': 99, 'description': 'Redirecting', 'result': dest_path }
