from django.contrib import admin
from .models import VimeoLiveStreams
from .models import VimeoVideos

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
        )}),
    )

    search_fields = ('day', 'name')
    order_by = ('time_from')

@admin.register(VimeoVideos)
class VimeoVideosAdmin(admin.ModelAdmin):
    model = VimeoVideos
    list_display = ('name', 'video_url', 'thumbnail_link', 'upload_date')
    fieldsets = (
        (None, {'fields': ('name', 'video_url', 'thumbnail_link', 'upload_date',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'video_url', 'thumbnail_link', 'upload_date',)}),
    )
    search_fields = ('name', 'video_url', 'upload_date')
    ordering = ('name',)

