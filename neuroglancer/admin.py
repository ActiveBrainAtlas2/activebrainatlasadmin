import json
import urllib
from urllib.parse import urlencode

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe

from neuroglancer.models import UrlModel
# Register your models here.

@admin.register(UrlModel)
class UrlModel(admin.ModelAdmin):
    list_display = ('animal', 'comments', 'open_neuroglancer','vetted','person', 'public', 'created')
    ordering = ['-created']
    readonly_fields = ['url', 'created', 'user_date']
    list_filter = ['created', 'public', 'vetted']
    search_fields = ['url', 'comments']


    def open_neuroglancer(self, obj):
        return format_html('<a target="_blank" href="https://activebrainatlas.ucsd.edu/ng/#!{}">Open in Neuroglancer</a>',
                           escape(obj.url))

    open_neuroglancer.short_description = 'Neuroglancer'
    open_neuroglancer.allow_tags = True
