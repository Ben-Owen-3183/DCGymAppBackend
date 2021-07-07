from django.contrib import admin
from .models import TimeTable

# Register your models here.
@admin.register(TimeTable)
class TimeTableAdmin(admin.ModelAdmin):
    model = TimeTable
    list_display = ('day', 'time_from', 'time_to', 'excercise', 'instructor', 'live', )

    list_filter = ('day', 'live')

    fieldsets = (
        (None, {'fields': (
            'day',
            'time_from',
            'time_to',
            'excercise',
            'instructor',
            'live'
        )}),
    )
    """
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff')}),
    )
    """
    search_fields = ('day', 'excercise', 'instructor')
    order_by = ('time_from')

# admin.site.register(TimeTable, TimeTableAdmin)
