from django.contrib import admin
from .models import Airport, Project

# Register your models here.


# class MyAdminSite(admin.AdminSite):
#     site_header = "Pegasus Admin"


admin.site.register(Airport)
admin.site.register(Project)