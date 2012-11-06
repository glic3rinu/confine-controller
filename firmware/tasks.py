from celery.task import task
from confw import confw
from django.db import transaction


def clean_files(self, *args, **kwargs):
    # TODO cleanup build.image file if fails
    pass


@task(name="firmware.build", on_failure=clean_files)
#@transaction.commit_on_success
def build(build_id):
    from firmware.models import Build, Config

    build_obj = Build.objects.get(pk=build_id)
    build_obj.task_id=build.request.id
    build_obj.save()
    
    from time import sleep
    sleep(6)
    
    config = Config.objects.get()
    # TODO how to get public_ipv4_avail ?
    base_image = config.get_image(build_obj.node)
#   template = confw.template('generic', 'confine', basedir='/tmp/templates/')
#   files = confw.files('generic', basedir='/tmp/files/')
    build_uci = []
    for config_uci in config.get_uci():
        value = config_uci.get_value(build_obj.node)
#       template.set(config_uci.section, config_uci.option, value)
        build_uci.append({
            'section': config_uci.section,
            'option': config_uci.option,
            'value': value})
#   image = confw.image(template, files)
#   image.build(base_image.path, gzip=True)
#   image.clean()
    # TODO iamge.path
    build_obj.image = base_image.name.replace('.img.', '-%s.img.' % build_obj.pk)
    build_obj.save()
    for uci in build_uci:
        build_obj.add_uci(**uci)
    
    return build_obj
