from state.models import State


def merge_nodata():
    merged = 0
    for state in State.objects.all():
        previous = None
        for record in state.history.order_by('start'):
            if (previous and (
                (record.value == State.NODATA and (record.end-record.start).total_seconds() < 120) or
                (previous.end == record.start and previous.value == record.value)) ):
                    previous.end = record.end
                    previous.save()
                    record.delete()
                    merged += 1
            else:
                previous = record
    print 'Total merged: %i' % merged
