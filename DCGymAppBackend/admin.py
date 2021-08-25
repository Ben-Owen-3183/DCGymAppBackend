
"""
from django.contrib import admin
# the module name is app_name.models
from login.models import CustomUser
# Register your models to admin site, then you can add, edit, delete and search your models in Django admin site.
admin.site.register(CustomUser)
<<<<<<< HEAD
=======

"""


from django.contrib import admin

class MyAdminSite(admin.AdminSite):
     site_header = 'Admin David Corfield Gymnasium'

admin_site = MyAdminSite(name='myadmin')
>>>>>>> development
