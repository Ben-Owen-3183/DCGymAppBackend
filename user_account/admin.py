from django.contrib import admin
from .models import MembershipStatus
from .models import MainJointAccount
from .models import LinkedAccount

# Register your models here.
@admin.register(MembershipStatus)
class MembershipStatusAdmin(admin.ModelAdmin):
    model = MembershipStatus
    list_display = ('email', 'active', 'api_type', 'customer_id', 'mandate_id', 'subscription_id')
    list_filter = (['api_type', 'active', ])
    search_fields = ('email', 'active', 'api_type', 'customer_id', 'mandate_id', 'subscription_id')


# Register your models here.
@admin.register(MainJointAccount)
class MainJointAccountAdmin(admin.ModelAdmin):
    model = MainJointAccount
    raw_id_fields = ("main_joint_account",)


# Register your models here.
@admin.register(LinkedAccount)
class LinkedAccountAdmin(admin.ModelAdmin):
    model = LinkedAccount
    list_display = ('child_account', 'parent_account', )
    raw_id_fields = ('parent_account', )
    raw_id_fields = ("child_account",)
