# TODO: create a management command that fills the default resources
# and invocate it on postupgradecontroller in order to fill i.e.
# nodes with their default disk space.
# http://redmine.confine-project.eu/issues/46#note-42

from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand, CommandError

from resources import ResourcePlugin
from resources.models import Resource

class Command(BaseCommand):
    option_list = BaseCommand.option_list
    help = 'Fills the default resources.'
    
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.option_list = BaseCommand.option_list
    
    def handle(self, *args, **options):
        for resource in ResourcePlugin.plugins:
            for producer in resource.producers:
                # get productor contentype
                app, model = producer.lower().split('.')
                content_type = ContentType.objects.get(app_label=app, model=model)
                model_class = content_type.model_class()
                
                # create resource for objects of this class
                # excluding ones with resource alreday defined!
                exclude = Resource.objects.filter(
                            name=resource.name,
                            content_type=content_type
                        ).values_list('object_id', flat=True)
                objects = model_class.objects.exclude(id__in=exclude)
                
                # insert into database
                resources = Resource.objects.bulk_create([
                    Resource(
                        name=resource.name, content_object=obj,
                        max_sliver=resource.max_sliver,
                        dflt_sliver=resource.dflt_sliver
                    )
                    for obj in objects
                ])
                
                self.stdout.write("%s %s -- Excluded: %i, Created: %i" %
                    (resource.name, producer, len(exclude), len(resources)))

                # TODO purge old resources

