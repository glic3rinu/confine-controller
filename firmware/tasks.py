from celery.task import task
from confw import confw
import os


@task(name="firmware.build")
def build(build_id):
    from firmware.models import Build, Config

    build_obj = Build.objects.get(pk=build_id)
    build_obj.task_id=build.request.id
    build_obj.save()
    config = Config.objects.get()
    base_image = config.get_image(build_obj.node)
    template = confw.template('generic', 'confine', basedir='/tmp/templates/')
#    files = confw.files()

    build_uci = []
    for config_uci in config.get_uci():
        value = config_uci.get_value(build_obj.node)
        template.set(config_uci.section, config_uci.option, value)
        build_uci.append({
            'section': config_uci.section,
            'option': config_uci.option,
            'value': value})
    
    image = confw.image(template=template)
    path = base_image.path.replace('.img.gz', '-%s.img' % build_obj.pk)
    try: image_path = image.build(base_image.path, userspace=True, output=path, gzip=True)
    except: 
        image.clean()
        raise
    image.clean()
    build_obj.image = os.path.relpath(image_path, start=base_image.storage.base_location)
    build_obj.save()
    for uci in build_uci:
        build_obj.add_uci(**uci)
    
    return typrimage_file
