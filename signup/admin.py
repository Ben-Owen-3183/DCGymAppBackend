from django.contrib import admin
from .models import PotentialUser
# Register your models here.


# Register your models here.
@admin.register(PotentialUser)
class PotentialUserAdmin(admin.ModelAdmin):
    model = PotentialUser
    list_display = ('email', 'first_name', 'last_name', 'locked', 'timestamp')
    list_filter = (['locked', ])
    search_fields = ('first_name', 'last_name', 'email', 'locked', 'timestamp')
