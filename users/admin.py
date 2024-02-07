from django.contrib import admin

from users.models import User


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    search_fields = ['username', 'email']


admin.site.register(User, UserAdmin)
