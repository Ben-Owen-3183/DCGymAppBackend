from django.contrib import admin
from .models import VimeoLiveStreams

# Register your models here.
@admin.register(VimeoLiveStreams)
class LiveStreamAdmin(admin.ModelAdmin):
    model = VimeoLiveStreams
    list_display = ('name', 'day', 'time_from', 'time_to')

    list_filter = (['day'])

    fieldsets = (
        (None, {'fields': (
            'name',
            'day',
            'time_from',
            'time_to',
            'stream_url',
            'chat_url',
        )}),
    )

    search_fields = ('day', 'name')
    order_by = ('time_from')

# admin.site.register(TimeTable, TimeTableAdmin)
