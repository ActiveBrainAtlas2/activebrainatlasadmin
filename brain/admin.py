from django.contrib import admin
from django.forms import TextInput, Textarea, DateInput, NumberInput
from django.db import models
import csv
from django.http import HttpResponse
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.html import format_html

from brain.forms import save_slide_model, TifInlineFormset
from brain.models import (Animal, Histology, Injection, Virus, InjectionVirus,
                          OrganicLabel, ScanRun, Slide, SlideCziToTif, Section)


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        excludes = ['histogram',  'image_tag']
        field_names = [field.name for field in meta.fields if field.name not in excludes]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"


class AtlasAdminModel(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'20'})},
        models.DateTimeField: {'widget': DateInput(attrs={'size':'20'})},
        # models.DateField: {'widget': DateTimeInput(attrs={'size':'20','type':'date'})},
        models.DateField: {'widget': AdminDateWidget(attrs={'size':'20'})},
        models.IntegerField: {'widget': NumberInput(attrs={'size':'20'})},
        models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    def is_active(self, instance):
        return instance.active == 1

    is_active.boolean = True

    list_filter = ('created', )
    fields = []
    actions = ["export_as_csv"]
    class Media:
        css = {
            'all': ('css/admin.css',)
        }


@admin.register(Animal)
class AnimalAdmin(AtlasAdminModel, ExportCsvMixin):
    list_display = ('prep_id', 'comments', 'histogram', 'created')
    search_fields = ('prep_id',)
    ordering = ['prep_id']
    exclude = ('created',)


    def histogram(self, obj):
        return format_html('<a target="_blank" href="https://activebrainatlas.ucsd.edu/data/{}/brains_info/histogram.html">Open</a>',
                           (obj.prep_id))

    histogram.short_description = 'Histogram'
    #histogram.allow_tags = True


@admin.register(Histology)
class HistologyAdmin(AtlasAdminModel, ExportCsvMixin):
    list_display = ('prep_id', 'label', 'performance_center')
    search_fields = ('prep_id',)
    autocomplete_fields = ['prep_id']
    ordering = ['prep_id', 'label']
    exclude = ('created',)

    def prep_id(self, instance):
        return instance.prep.prep_id

@admin.register(Injection)
class InjectionAdmin(AtlasAdminModel, ExportCsvMixin):
    list_display = ('prep_id', 'performance_center', 'anesthesia', 'comments', 'created')
    search_fields = ('prep_id',)
    ordering = ['created']

    def prep_id(self, instance):
        return instance.prep.prep_id

@admin.register(Virus)
class VirusAdmin(AtlasAdminModel, ExportCsvMixin):
    list_display = ('virus_name', 'virus_type', 'type_details', 'created')
    search_fields = ('virus_name',)
    ordering = ['virus_name']

@admin.register(InjectionVirus)
class InjectionVirusAdmin(AtlasAdminModel):
    list_display = ('prep_id', 'injection_comments', 'virus_name', 'created')
    fields = ['injection', 'virus']
    search_fields = ('prep_id',)
    ordering = ['created']


    def prep_id(self, instance):
        return instance.injection.prep.prep_id

    def injection_comments(self, instance):
        return instance.injection.comments

    def virus_name(self, instance):
        return instance.virus.virus_name

@admin.register(OrganicLabel)
class OrganicLabelAdmin(AtlasAdminModel, ExportCsvMixin):
    list_display = ('label_id', 'label_type', 'type_details', 'created')
    search_fields = ('label_id',)
    ordering = ['label_id', 'label_type', 'type_details', 'created']

@admin.register(ScanRun)
class ScanRunAdmin(AtlasAdminModel, ExportCsvMixin):
    list_display = ('prep_id', 'performance_center', 'machine','comments', 'created')
    search_fields = ('prep_id',)
    ordering = ['prep_id', 'performance_center', 'machine','comments', 'created']

    def prep_id(self, instance):
        return instance.prep.prep_id


class TifInline(admin.TabularInline):
    model = SlideCziToTif
    fields = ('scene_number', 'scene_index', 'channel', 'active')
    readonly_fields = ['scene_number', 'channel', 'scene_index']
    ordering = ['-active', 'scene_number', 'scene_index']
    extra = 0
    can_delete = False
    formset = TifInlineFormset

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(TifInline, self).get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

    def get_queryset(self, request):
        qs = super(TifInline, self).get_queryset(request)
        return qs.filter(active=1).filter(channel=1)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return True

@admin.register(Slide)
class SlideAdmin(AtlasAdminModel, ExportCsvMixin):
    list_display = ('prep_id', 'file_name', 'slide_status', 'scene_qc_1', 'scene_qc_2', 'scene_qc_3', 'scene_qc_4', 'scene_count')
    search_fields = ['scan_run__prep__prep_id', 'file_name']
    ordering = ['file_name', 'created']
    readonly_fields = ['file_name', 'slide_physical_id', 'scan_run', 'processed', 'file_size']


    def get_fields(self, request, obj):
        count = self.scene_count(obj)
        fields = ['file_name', 'scan_run', 'slide_physical_id', 'slide_status', 'rescan_number',
                  'insert_before_one', 'scene_qc_1',
                  'insert_between_one_two', 'scene_qc_2']

        scene_3_fields = ['insert_between_two_three', 'scene_qc_3']
        scene_4_fields = ['insert_between_three_four', 'scene_qc_4']
        scene_5_fields = ['insert_between_four_five', 'scene_qc_5']
        scene_6_fields = ['insert_between_five_six', 'scene_qc_6']
        if count > 2:
            fields.extend(scene_3_fields)
        if count > 3:
            fields.extend(scene_4_fields)
        if count > 4:
            fields.extend(scene_5_fields)
        if count > 5:
            fields.extend(scene_6_fields)

        last_fields = ['comments', 'processed']
        fields.extend(last_fields)
        return fields

    inlines = [TifInline, ]

    class Media:
        css = {"all": ("css/admin.css",)}

    def scene_count(self, obj):
        count = SlideCziToTif.objects.filter(slide_id=obj.id).filter(channel=1).filter(active=True).count()
        return count

    scene_count.short_description = "Active Scenes"

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        save_slide_model(self, request, obj, form, change)
        super().save_model(request, obj, form, change)


    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


    def prep_id(self, instance):
        return instance.scan_run.prep.prep_id

@admin.register(SlideCziToTif)
class SlideCziToTifAdmin(AtlasAdminModel, ExportCsvMixin):
    list_display = ('file_name', 'scene_number', 'channel','file_size')
    ordering = ['file_name', 'scene_number', 'channel', 'file_size']
    exclude = ['processing_duration']
    readonly_fields = ['file_name', 'scene_number','slide','scene_index', 'channel', 'file_size', 'width','height']
    search_fields = ['file_name']


    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


class ExportSections:
    def export_sections(self, request, queryset):
        meta = self.model._meta
        headers = ['File name', 'Slide', 'Scene']
        fields = ['file_name', 'slide', 'scene']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(headers)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in fields])

        return response

    export_sections.short_description = "Export Selected"

@admin.register(Section)
class SectionAdmin(AtlasAdminModel, ExportCsvMixin):
    #change_list_template = "admin/section/qc.html"
    indexCounter = -1
    list_display = ('tif','section_number', 'slide','scene', 'histogram', 'image_tag')
    ordering = ['prep_id', 'channel']
    list_filter = []
    list_display_links = None
    search_fields = ['prep_id', 'file_name']
    #actions = ["export_sections"]
    list_per_page = 1000
    class Media:
        css = {
            'all': ('admin/css/thumbnail.css',)
        }

    def section_number(self, instance):
        self.indexCounter += 1
        return self.indexCounter

    section_number.short_description = 'Section'


    def get_queryset(self, request, obj=None):
        self.indexCounter = -1
        sections = Section.objects.filter(prep_id='XXXX')
        if request and request.GET:
            prep_id = request.GET['q']
            histology = Histology.objects.get(prep_id=prep_id)
            orderby = histology.side_sectioned_first

            if orderby == 'DESC':
                sections =  Section.objects.filter(prep_id__exact=prep_id).filter(channel=1)\
                    .order_by('-slide_physical_id', '-scene_number')
            else:
                sections = Section.objects.filter(prep_id__exact=prep_id).filter(channel=1)\
                    .order_by('slide_physical_id', 'scene_number')

        return sections

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.site_header = 'Active Brain Atlas Admin'
admin.site.site_title = "Active Brain Atlas"
admin.site.index_title = "Welcome to Active Brain Atlas Portal"

