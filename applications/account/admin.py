from django.contrib import admin

from applications.account.models import CustomUser

# Register your models here.
admin.site.register(CustomUser)