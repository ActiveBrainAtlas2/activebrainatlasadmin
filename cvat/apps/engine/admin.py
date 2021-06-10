
# Copyright (C) 2018 Intel Corporation
#
# SPDX-License-Identifier: MIT

from django.contrib import admin
from .models import Task, Segment, Job, Label, AttributeSpec
from django.conf import settings
from django.utils.html import format_html, escape

class JobInline(admin.TabularInline):
    model = Job
    can_delete = False

    # Don't show extra lines to add an object
    def has_add_permission(self, request, object=None):
        return False

class SegmentInline(admin.TabularInline):
    model = Segment
    show_change_link = True
    readonly_fields = ('start_frame', 'stop_frame')
    can_delete = False

    # Don't show extra lines to add an object
    def has_add_permission(self, request, object=None):
        return False


class AttributeSpecInline(admin.TabularInline):
    model = AttributeSpec
    extra = 0
    max_num = None

class LabelInline(admin.TabularInline):
    model = Label
    show_change_link = True
    extra = 0
    max_num = None

class LabelAdmin(admin.ModelAdmin):
    # Don't show on admin index page
    def has_module_permission(self, request):
        return False

    inlines = [
        AttributeSpecInline
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

class SegmentAdmin(admin.ModelAdmin):
    # Don't show on admin index page
    def has_module_permission(self, request):
        return False

    inlines = [
        JobInline
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class TaskAdmin(admin.ModelAdmin):
    #date_hierarchy = 'updated_date'
    list_display_links = None
    list_filter = ['created_date']
    readonly_fields = ('created_date', 'updated_date', 'overlap')
    list_display = ('open_in_cvat', 'mode', 'owner', 'assignee', 'created_date')
    search_fields = ('name', 'mode', 'owner__username', 'owner__first_name',
        'owner__last_name', 'owner__email', 'assignee__username', 'assignee__first_name',
        'assignee__last_name')
    inlines = [
        SegmentInline,
        LabelInline
    ]

    # Don't allow to add a task because it isn't trivial operation
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def open_in_cvat(self, obj):
        host = "http://muralis.dk.ucsd.edu"
        #if settings.DEBUG:
        #    host = "http://127.0.0.1:8080"

        #http://muralis.dk.ucsd.edu/tasks/41
        links = f'<a target="_blank" href="{host}/tasks/{obj.id}">{obj.name}</a>'
        return format_html(links)


admin.site.register(Task, TaskAdmin)
admin.site.register(Segment, SegmentAdmin)
admin.site.register(Label, LabelAdmin)
