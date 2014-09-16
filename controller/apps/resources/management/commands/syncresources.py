from optparse import make_option

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from resources import ResourcePlugin
from resources.models import Resource

class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = 'Sync existing resources with the database.'
    
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list + (
            make_option('--override', action='store_true', dest='override', default=False,
                help='Override current resources max_req and dflt_req'),)
    
    def handle(self, *args, **options):
        self.stdout.write("== Sync existing resource plugins ==")
        existing_pks = []
        override = options.get('override')
        for resource in ResourcePlugin.plugins:
            for producer in resource.producers:
                # get productor contentype
                app, model = producer.lower().split('.')
                content_type = ContentType.objects.get(app_label=app, model=model)
                model_class = content_type.model_class()
                
                # create (or override) resource for objects of this class
                skipped = updated = 0
                for obj in model_class.objects.all():
                    #FIXME use update_or_create when upgrading to django 1.7
                    # https://docs.djangoproject.com/en/1.7/ref/models/querysets/#update-or-create
                    instance, created = Resource.objects.get_or_create(
                                            name=resource.name,
                                            content_type=content_type,
                                            object_id=obj.id,
                                            defaults={
                                                'max_req': resource.max_req,
                                                'dflt_req': resource.dflt_req
                                            }
                                        )
                    if override:
                        instance.max_req = resource.max_req
                        instance.dflt_req = resource.dflt_req
                    if created or override:
                        instance.save()
                        updated +=1
                    else:
                        skipped += 1
                    existing_pks.append(instance.pk)
                
                self.stdout.write("\t%s > %s -- skipped: %i, updated: %i" %
                    (resource.name, producer, skipped, updated))
        
        # Purge old resource plugins
        old_resources = Resource.objects.exclude(pk__in=existing_pks)
        self.stdout.write("\tPurged resources: %i" % old_resources.count())
        old_resources.delete()

