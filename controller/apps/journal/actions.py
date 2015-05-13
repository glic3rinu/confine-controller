from django.shortcuts import redirect


def show_node_slivers_journal(modeladmin, request, queryset):
    try:
        node = queryset.get()
    except ObjectDoesNotExist:
        raise Http404
    return redirect('public_node_sliver_list', node.id)

show_node_slivers_journal.url_name = 'slivers-journal'
show_node_slivers_journal.verbose_name = "Slivers' journal"
show_node_slivers_journal.description = "Show the journal of slivers run at this node."
show_node_slivers_journal.always_display = True

