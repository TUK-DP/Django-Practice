from django.contrib import admin

from diary.models import Diary


class DiaryAdmin(admin.ModelAdmin):
    search_fields = ['title', 'content']


# Register your models here.
admin.site.register(Diary, DiaryAdmin)
