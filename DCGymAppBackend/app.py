from django.contrib.admin.apps import AdminConfig

class MyAdminConfig(AdminConfig):
    default_site = 'DCGymAppBackend.admin.MyAdminSite'
