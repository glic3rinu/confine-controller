from celery.task import task

@task(name="Generate Firmware")
def generate_firmware(node):
    return "NOT IMPLEMENTED"
