from django.contrib import admin

from neuroglancer.models import UrlModel
# Register your models here.

@admin.register(UrlModel)
class SlideCziToTifAdmin(admin.ModelAdmin):
    list_display = ('short_description', 'comments', 'active', 'created')
    ordering = ['url', 'active', 'created']
    list_filter = ['created']

