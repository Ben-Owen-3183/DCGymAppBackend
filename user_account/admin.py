from django.contrib import admin
from .models import MembershipStatus, AwaitingActivation, PasswordResets

# Register your models here.
@admin.register(PasswordResets)
class PasswordResetsAdmin(admin.ModelAdmin):
    model = PasswordResets
    list_display = ('email', 'locked', 'timestamp', 'user', )
    list_filter = (['locked', ])
    search_fields = ('email', 'locked', 'timestamp', 'user',)


# Register your models here.
@admin.register(MembershipStatus)
class MembershipStatusAdmin(admin.ModelAdmin):
    model = MembershipStatus
    list_display = ('email', 'active', )
    list_filter = (['active'])
    search_fields = ('email', 'active' )
    # change_list_template = 'admin/membership_status/membership_status_upload_members.html'


# Register your models here.
@admin.register(AwaitingActivation)
class AwaitingActivationAdmin(admin.ModelAdmin):
    model = AwaitingActivation
    list_display = ('name', 'user')
    search_fields = ('name', 'user')
    change_form_template = 'admin/membership_status/form_view.html'

    def get_osm_info(self):
        # ...
        pass

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['osm_data'] = self.get_osm_info()
        return super().change_view(
            request, object_id, form_url, extra_context=extra_context,
        )