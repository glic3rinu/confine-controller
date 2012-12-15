from django.contrib import admin

from .models import TimeSerie

class TimeSerieAdmin(admin.ModelAdmin):
    list_display = ['__unicode__', 'data', 'time', 'metadata']
    list_filter = ['content_type']
    date_hierarchy = 'time'

admin.site.register(TimeSerie, TimeSerieAdmin)
