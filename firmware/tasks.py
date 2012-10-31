from celery.task import task
from confw import confw


# TODO transaction wrapper?

@task(name="Build Firmware")
def build(config_id, node_id):
    from firmware.models import Config, Build
    from nodes.models import Node

    config = Config.objects.get(pk=config_id)
    node = Node.objects.get(pk=node_id)

    # TODO how to get public_ipv4_avail ?
    base_image = config.get_image(node)
#   template = confw.template('generic', 'confine', basedir='/tmp/templates/')
#   files = confw.files('generic', basedir='/tmp/files/')
    build_uci = []
    for config_uci in config.get_uci():
        value = config_uci.get_value(node)
#       template.set(config_uci.section, config_uci.option, value)
        build_uci.append({
            'section': config_uci.section,
            'option': config_uci.option,
            'value': value})
#   image = confw.image(template, files)
#   image.build(base_image.path, gzip=True)
#   image.clean()
    # TODO iamge.path
    # Create Build object
    build = Build.objects.create(node=node, version=config.version,
        image='firmwares/openwrt-x86-generic-combined-ext4-40.img.gz')
    for uci in build_uci:
        build.add_uci(**uci)

