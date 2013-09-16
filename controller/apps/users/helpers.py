from django.db.models import Q

from controller.forms.widgets import ReadOnlyWidget

from .models import Group


def filter_group_queryset(form, obj, user, query):
    if obj and obj.pk:
        # Add actual group
        query = Q( query | Q(pk=obj.group.pk) )
    if user.is_superuser:
        # TODO filter only user related groups + current obj group?
        groups = Group.objects.filter(query).distinct()
    else:
        groups = user.groups.filter(query).distinct()
    num_groups = len(groups)
    if num_groups >= 1:
        # User has can add obj in more than one group
        form.base_fields['group'].queryset = groups
    if num_groups == 1:
        # User can add obj in only one group (set that group by default)
        ro_widget = ReadOnlyWidget(groups[0].id, groups[0].name)
        form.base_fields['group'].widget = ro_widget
        form.base_fields['group'].required = False
    if num_groups == 0 and not user.is_superuser:
        raise Exception('Oops this is unfortunate but you can not proceed.')
    return form
