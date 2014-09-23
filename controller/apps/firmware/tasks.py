import os

from celery import states
from celery.task import task

from controller.models.utils import get_file_field_base_path

from .helpers import pem2der_string
from .image import Image


def update_state(build, progress, next, description):
    build.update_state(state=states.STARTED,
        meta={'progress': progress, 'next': next, 'description': description})


@task(name="firmware.build")
def build(build_id, *args, **kwargs):
    """ Builds a firmware image for build.node, excluding exclude files """
    # Avoid circular imports
    from firmware.models import Build, Config
    
    exclude = kwargs.get('exclude', [])
    
    # retrieve the existing build instance, used for user feedback
    update_state(build, 1, 4, 'Build started')
    build_obj = Build.objects.get(pk=build_id)
    build_obj.task_id = build.request.id
    build_obj.save()
    
    config = Config.objects.get()
    node = build_obj.node
    image = Image(build_obj.base_image.path)
    
    try:
        # Build the image
        image.prepare()
        
        update_state(build, 5, 14, 'Unpackaging base image')
        image.gunzip()
        
        update_state(build, 15, 29, 'Preparing image file system')
        image.mount()
        
        # handle registry api #245: put cert content into firmware image
        build_file = build_obj.files.get(path='/etc/confine/registry-server.crt')
        image.create_file(build_file)
        
        files = config.eval_files(node, exclude=exclude, image=image)
        total = len(files)
        for num, build_file in enumerate(files):
            current = 30 + num/total*25
            next = min(30 + (num+1)/total*25, 59)
            update_state(build, current, next, 'Generating %s file' % build_file.name)
            image.create_file(build_file)
            build_file.build = build_obj
            build_file.save()
        
        # generate binary versions of uhttpd key and certificate #410
        from .models import BuildFile # avoid circular imports
        for pem_path in ['/etc/uhttpd.crt.pem', '/etc/uhttpd.key.pem']:
            try:
                pem_file = build_obj.files.get(path=pem_path)
            except BuildFile.DoesNotExist:
                pass
            else:
                der_content = pem2der_string(pem_file.content)
                der_path = pem_path.rstrip('.pem')
                der_file = BuildFile(path=der_path, content=der_content, config=pem_file.config)
                image.create_file(der_file)
        
        plugins = config.plugins.active()
        total = len(plugins)
        for num, plugin in enumerate(plugins):
            plugin.instance.pre_umount(image, build_obj, *args, **kwargs)
        
        update_state(build, 60, 74, 'Unmounting image file system')
        image.umount()
        
        # Post umount
        for num, plugin in enumerate(plugins):
            # FIXME this progress is not correct
            current = 75 + num/total*25
            next = min(75 + (num+1)/total*25, 80)
            instance = plugin.instance
            update_state(build, current, next, instance.post_umount.__doc__)
            instance.post_umount(image, build_obj, *args, **kwargs)
        
        update_state(build, 80, 94, 'Compressing image')
        image.gzip()
        
        update_state(build, 95, 99, 'Cleaning up')
        
        # Image name
        image_name = config.get_image_name(node, build_obj)
        for plugin in config.plugins.active():
            image_name = plugin.instance.update_image_name(image_name, **kwargs)
        base_path = get_file_field_base_path(Build, 'image')
        dest_path = os.path.join(base_path, image_name)
        image.move(dest_path)
    finally:
        image.clean()
    
    build_obj.image = dest_path
    build_obj.save()
    return { 'progress': 100, 'description': 'Redirecting', 'result': dest_path }
