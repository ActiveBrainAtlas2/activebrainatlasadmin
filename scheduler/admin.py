from django.contrib import admin
# Register your models here.
from django.forms import DateTimeInput
from django import forms

from django.utils.html import format_html
from django.db import models
from django.contrib.admin.widgets import AdminTimeWidget, AdminSplitDateTime, AdminDateWidget

from scheduler.models import Location, Schedule


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('room', 'description', 'people', 'people_allowed')
    ordering = ['room', 'description']


    def people(self, obj):
        persons = []
        for person in obj.primary_people.all():
            persons.append(person.username)
        html = ", ".join(persons)
        return format_html(html)

    people.short_description = 'Primary People'

class MyAdminTimeWidget(AdminTimeWidget):
    class Media:
        js = ('js/clock_time_selections.js',)


class MyAdminSplitDateTime(AdminSplitDateTime):
    def __init__(self, attrs=None):
        widgets = [AdminDateWidget, MyAdminTimeWidget]
        forms.MultiWidget.__init__(self, widgets, attrs)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    change_form_template = "schedule.html"
    list_display = ('location', 'start_time', 'end_time', 'person')
    ordering = ['-start_time', '-end_time', 'location', 'person']
    exclude = ['person', 'active']
    list_filter = ('start_time', )
    formfield_overrides = {
        models.DateTimeField: {'widget': MyAdminSplitDateTime(attrs={'size': '10'})},
    #    # models.DateTimeField: {'widget': MyAdminSplitDateTime},
    }

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        super().save_model(request, obj, form, change)

