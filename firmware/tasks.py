import os

from celery.task import task
from confw import confw


@task(name="firmware.build")
def build(build_id):
    from firmware.models import Build, Config

    build_obj = Build.objects.get(pk=build_id)
    build_obj.task_id=build.request_id
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
    image_name = base_image.name.replace('.img.gz', '-%s.img' % build_obj.pk)
    image_path = os.path.join(build_obj.image.storage.location, image_name)
    try: image_path = image.build(base_image.path, userspace=True, output=image_path, gzip=True)
    except: 
        image.clean()
        raise
    image.clean()
    build_obj.image = image_name + '.gz'
    build_obj.save()
    for uci in build_uci:
        build_obj.add_uci(**uci)
    
    return image_path
