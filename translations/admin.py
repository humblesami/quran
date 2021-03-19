from django.contrib import admin
from .models import Sura, Aya


class SuraAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


class AyaAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


class AyatestAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__']


admin.site.register(Sura, SuraAdmin)
admin.site.register(Aya, AyaAdmin)

