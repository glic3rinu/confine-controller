from celery.task import task

@task(name="generate_firmware")
def generate_firmware(node):
    return "NOT IMPLEMENTED"
