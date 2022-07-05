import os

from django.contrib import admin
from django.forms import TextInput, Textarea, DateInput, NumberInput, Select
from django.db import models
import csv
from django.http import HttpResponse
from django.contrib.admin.widgets import AdminDateWidget
from django.utils.safestring import mark_safe

from brain.forms import save_slide_model, TifInlineFormset
from brain.models import (Animal, Histology, Injection, Virus, InjectionVirus,
                          OrganicLabel, ScanRun, Slide, SlideCziToTif, Section)


class AtlasAdminModel(admin.ModelAdmin):
    """This is used as a base class for most of the other classes. It contains
    all the common variables that all the tables/objects have. It inherits
    from the Django base admin model: admin.ModelAdmin
    """
    class Media:
        """This is a simple class that defines some CSS attributes for the 
        thumbnails
        """
        css = {
            'all': ('admin/css/thumbnail.css',)
        }

    def is_active(self, instance):
        """A method returning a boolean showing if the data row is active

        :param instance: obj class
        :return: A boolean
        """
        return instance.active == 1

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Simple formatting for foreign keys

        :param db_field: data row field
        :param request: http request
        :param kwargs: extra args
        :return: the HTML of the form field
        """
        kwargs['widget'] = Select(attrs={'style': 'width: 250px;'})
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


    formfield_overrides = {
        models.CharField: {'widget': Select(attrs={'size': '20', 'style': 'width:250px;'})},
        models.CharField: {'widget': TextInput(attrs={'size': '20','style': 'width:100px;'})},
        models.DateTimeField: {'widget': DateInput(attrs={'size': '20'})},
        models.DateField: {'widget': AdminDateWidget(attrs={'size': '20'})},
        models.IntegerField: {'widget': NumberInput(attrs={'size': '40', 'style': 'width:100px;'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }

    is_active.boolean = True
    list_filter = ('created', )
    fields = []
    actions = ["export_as_csv"]


class ExportCsvMixin:
    """A class used by most of the admin categories. It adds formatting 
    to make fields look consistent and also adds the method to export 
    to CSV from each of the 'Action' dropdowns in each category. 
    """

    def export_as_csv(self, request, queryset):
        """Set the callback function to be executed when the device sends a
        notification to the client.

        :param request: The http request
        :param queryset: The query used to fetch the CSV data
        :return: a http response
        """

        meta = self.model._meta
        excludes = ['histogram',  'image_tag']
        field_names = [
            field.name for field in meta.fields if field.name not in excludes]
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(
            meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field)
                                  for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"



@admin.register(Animal)
class AnimalAdmin(AtlasAdminModel, ExportCsvMixin):
    """This class is used to administer the animal. It includes all the metadata
    entered by the user. The animal class is often used as a key in another table.
    """

    list_display = ('prep_id', 'comments', 'histogram', 'created')
    search_fields = ('prep_id',)
    ordering = ['prep_id']
    exclude = ('created',)

@admin.register(Histology)
class HistologyAdmin(AtlasAdminModel, ExportCsvMixin):
    """A class to administer the histology of each animal

    :Inheritance:
        :AtlasAdminModel: The base admin model
        :ExportCsvMixin: The class with standard features and CSV 
            exporter method.

    """
    list_display = ('prep_id', 'label', 'performance_center')
    search_fields = ('prep__prep_id',)
    autocomplete_fields = ['prep_id']
    ordering = ['prep_id', 'label']
    exclude = ('created',)

@admin.register(Injection)
class InjectionAdmin(AtlasAdminModel, ExportCsvMixin):
    """A class to describe the injections (if any) for each animal. 
    Each animal can have multiple injections.

    :Inheritance:
        :AtlasAdminModel: The base admin model
        :ExportCsvMixin: The class with standard features and CSV 
            exporter method.

    """
    list_display = ('prep_id', 'performance_center', 'anesthesia', 'comments', 'created')
    search_fields = ('prep__prep_id',)
    ordering = ['created']

@admin.register(Virus)
class VirusAdmin(AtlasAdminModel, ExportCsvMixin):
    """A class used to describe a virus. This class can then be a 
    foreign key into the Injection class

    :Inheritance:
        :AtlasAdminModel: The base admin model
        :ExportCsvMixin: The class with standard features and CSV 
            exporter method.

    """
    list_display = ('virus_name', 'virus_type', 'type_details', 'created')
    search_fields = ('virus_name',)
    ordering = ['virus_name']

@admin.register(InjectionVirus)
class InjectionVirusAdmin(AtlasAdminModel):
    """This class describes a many to many relationship between the 
    virus and the injection classes. An animal can multiple 
    injections, with each injection having one or more viruses.

    :Inheritance:
        :AtlasAdminModel: The base admin model

    """
    list_display = ('prep_id', 'injection_comments', 'virus_name', 'created')
    fields = ['injection', 'virus']
    search_fields = ('injection__prep__prep_id',)
    ordering = ['created']

    def prep_id(self, instance):
        """This returns the animal name (string) used as a
        foreign key in this class.

        :param instance: the obj
        :return: the prep_id (AKA the animal name) as a string
        """
        return instance.injection.prep.prep_id

    def injection_comments(self, instance):
        """This gives the description from 
        the injection foreign key

        :param instance: the obj
        :return: a string that contains the comments
        """
        return instance.injection.comments

    def virus_name(self, instance):
        """Gives the description from the virus foreign key

        :param instance: the obj
        """
        return instance.virus.virus_name

@admin.register(OrganicLabel)
class OrganicLabelAdmin(AtlasAdminModel, ExportCsvMixin):
    """Description of OrganicLabelAdmin
    This class describes the organice label for an animal. So far, 
    it has had no data entered in it.

    :Inheritance:
        :AtlasAdminModel: The base admin model
        :ExportCsvMixin: The class with standard features and CSV 
            exporter method.
    """
    list_display = ('label_id', 'label_type', 'type_details', 'created')
    search_fields = ('label_id',)
    ordering = ['label_id', 'label_type', 'type_details', 'created']

@admin.register(ScanRun)
class ScanRunAdmin(AtlasAdminModel, ExportCsvMixin):
    """This class describes what occurs when the slides are actually 
    scanned. Many of the attributes from this class are used 
    throughout the preprocessing pipeline. An animal can have multiple
    scan runs, but usually, there is just one scanning done 
    for each animal.

    :Inheritance:
        :AtlasAdminModel: The base admin model
        :ExportCsvMixin: The class with standard features and CSV 
            exporter method.
    """
    list_display = ('prep_id', 'performance_center', 'machine','comments', 'created')
    search_fields = ('prep__prep_id',)
    ordering = ['prep_id', 'performance_center', 'machine','comments', 'created']

class TifInline(admin.TabularInline):
    """This class is solely used for the database QA. It will display the 
    associated TIFF files for each 
    slide on the slide page.

    :Inheritance:
        :admin.TabularInline: The class that describes how the data is 
            laid out on the page.
    """
    model = SlideCziToTif
    fields = ('file_name','scene_number', 'scene_index', 'channel', 'scene_image', 'section_image')
    readonly_fields = ['file_name', 'scene_number', 'channel', 'scene_index', 'scene_image', 'section_image']
    ordering = ['-active', 'scene_number', 'scene_index']
    extra = 0
    can_delete = False
    formset = TifInlineFormset
    template = 'tabular_tifs.html'

    def scene_image(self, obj):
        """This method tests if there is a 
        PNG file for each scene, and if so, shows it on the QA page 
        for each slide. This is very helpful when the user must decide
        if the TIFF file is usable.

        :param obj: the TIFF obj
        :return: HTML that displays a link to the scene PNG file
        """
        animal = obj.slide.scan_run.prep_id
        tif_file = obj.file_name
        png = tif_file.replace('tif', 'png')
        # DK55_slide112_2020_09_21_9205_S1_C1.png
        testfile = f"/net/birdstore/Active_Atlas_Data/data_root/pipeline_data/{animal}/www/scene/{png}"
        if os.path.isfile(testfile):
            thumbnail = f"https://activebrainatlas.ucsd.edu/data/{animal}/www/scene/{png}"
            return mark_safe(
                '<div class="profile-pic-wrapper"><img src="{}" /></div>'.format(thumbnail))
        else:
            return mark_safe('<div>Not available</div>')

    scene_image.short_description = 'Pre Image'

    def section_image(self, obj):
        """This method shows the TIFF image as 
        a PNG later on in the QA process after it has been cleaned and aligned.

        :param obj: the TIFF obj
        :return: HTML that displays a link to the scene PNG file
        """
        animal = obj.slide.scan_run.prep_id
        tif_file = obj.file_name
        png = tif_file.replace('tif', 'png')
        # DK55_slide112_2020_09_21_9205_S1_C1.png
        testfile = f"/net/birdstore/Active_Atlas_Data/data_root/pipeline_data/{animal}/www/{png}"
        if os.path.isfile(testfile):
            thumbnail = f"https://activebrainatlas.ucsd.edu/data/{animal}/www/{png}"
            return mark_safe(
                '<div class="profile-pic-wrapper"><img src="{}" /></div>'.format(thumbnail))
        else:
            return mark_safe('<div>Not available</div>')

    section_image.short_description = 'Post Image'


    def get_formset(self, request, obj=None, **kwargs):
        """Description of get_formset - sets up the form for the set of 
        TIFF files for each slide

        :param request: http request
        :param obj: the TIFF obj
        :param kwargs: extra args
        :return: the HTML of the formset
        """
        formset = super(TifInline, self).get_formset(request, obj, **kwargs)
        formset.request = request
        return formset

    def get_queryset(self, request):
        """Description of get_queryset - returns just the first channel 
        for each slide. We only need to look
        at the first channel for QA purposes.

        :param obj: the TIFF obj
        :return: a query set
        """
        qs = super(TifInline, self).get_queryset(request)
        return qs.filter(active=1).filter(channel=1)

    def has_add_permission(self, request, obj=None):
        """TIFF files cannot be added 
        at this stage.

        :param request: http request
        :param obj: the TIFF obj
        :return: False
        """
        return False

    def has_change_permission(self, request, obj=None):
        """TIFF files can be edited at this stage.

        :param request: http request
        :param obj: the TIFF obj
        :return: True
        """
        return True

@admin.register(Slide)
class SlideAdmin(AtlasAdminModel, ExportCsvMixin):
    """This class describes the admin area for a particular slide. This 
    is used in the QA process and includes
    the inline TIFF files in the QA form.

    :Inheritance:
        :AtlasAdminModel: The base admin model
        :ExportCsvMixin: The class with standard features and CSV 
            exporter method.
    """
    list_display = ('prep_id', 'file_name', 'slide_status', 'scene_qc_1', 'scene_qc_2', 'scene_qc_3', 'scene_qc_4', 'scene_count')
    search_fields = ['scan_run__prep__prep_id', 'file_name']
    ordering = ['file_name', 'created']
    readonly_fields = ['file_name', 'slide_physical_id', 'scan_run', 'processed', 'file_size']


    def get_fields(self, request, obj):
        """This method fetches the correct 
        number of inline TIFF files that are used
        in the QA form.

        :param request: http request
        :param obj: the TIFF obj
        :return: HTML of the fields
        """
        count = self.scene_count(obj)
        fields = ['file_name', 'scan_run', 'slide_physical_id', 'slide_status', 'rescan_number',
                  'insert_before_one', 'scene_qc_1','scene_rotation_1',
                  'insert_between_one_two', 'scene_qc_2','scene_rotation_2']

        scene_3_fields = ['insert_between_two_three', 'scene_qc_3','scene_rotation_3']
        scene_4_fields = ['insert_between_three_four', 'scene_qc_4','scene_rotation_4']
        scene_5_fields = ['insert_between_four_five', 'scene_qc_5','scene_rotation_5']
        scene_6_fields = ['insert_between_five_six', 'scene_qc_6','scene_rotation_6']
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

    def scene_count(self, obj):
        """Determines how many scenes are 
        there for a slide

        :param obj: the slide obj
        :return: an integer of the number of scenes
        """
        scenes = SlideCziToTif.objects.filter(slide__id=obj.id).filter(channel=1).values_list('scene_index').distinct()
        count = len(scenes)
        return count

    scene_count.short_description = "Active Scenes"

    def save_model(self, request, obj, form, change):
        """Description of save_model - overridden method of the save 
        method. When the user changes the scenes via the QA form, 
        the usual save isn't sufficient so we override it.

        :param self: the admin slide obj
        :param request: the http request
        :param obj: the slide obj
        :param form: the form obj
        :param change: if the form has changed or not.
        """
        obj.user = request.user
        save_slide_model(self, request, obj, form, change)
        super().save_model(request, obj, form, change)


    def has_delete_permission(self, request, obj=None):
        """Cannot show or use the delete button at this stage.

        :param request: http request
        :param obj: the slide obj
        :return: False
        """
        return False

    def has_add_permission(self, request, obj=None):
        """Cannot show or use the add button at this stage

        :param request: http request
        :param obj: the TIFF obj
        :return: False
        """
        return False


    def prep_id(self, instance):
        """Returns the animal name that the slide belongs to

        :param instance: the TIFF obj
        :return: False
        """
        return instance.scan_run.prep.prep_id

@admin.register(SlideCziToTif)
class SlideCziToTifAdmin(AtlasAdminModel, ExportCsvMixin):
    """A class to administer the individual scene, AKA the TIFF file.

    :Inheritance:
        :AtlasAdminModel: The base admin model
        :ExportCsvMixin: The class with standard features and CSV 
            exporter method.
    """
    list_display = ('file_name', 'scene_number', 'channel','file_size')
    ordering = ['file_name', 'scene_number', 'channel', 'file_size']
    exclude = ['processing_duration']
    readonly_fields = ['file_name', 'scene_number','slide','scene_index', 'channel', 'file_size', 'width','height']
    search_fields = ['file_name']


    def has_delete_permission(self, request, obj=None):
        """Cannot show or use the delete button at this stage

        :param request: http request
        :param obj: the TIFF obj
        :return: False
        """
        return False

    def has_add_permission(self, request, obj=None):
        """Cannot show or use the add button at this stage

        :param request: http request
        :param obj: the TIFF obj
        :return: False
        """
        return False


@admin.register(Section)
class SectionAdmin(AtlasAdminModel, ExportCsvMixin):
    """This class describes the Section methods and attributes. 
    Sections come from a view and 
    not a table so it needs to be handled a bit differently.

    :Inheritance:
        :AtlasAdminModel: The base admin model
        :ExportCsvMixin: The class with standard features and CSV
            exporter method.
    """
    indexCounter = -1
    list_display = ('tif','section_number', 'slide','scene', 'scene_index', 'histogram', 'image_tag')
    ordering = ['prep_id', 'channel']
    list_filter = []
    list_display_links = None
    search_fields = ['prep_id', 'file_name']
    list_per_page = 1000
    class Media:
        css = {'all': ('admin/css/thumbnail.css',)}

    def section_number(self, instance):
        """ Description of section_number - this is just an ordered query,
        so to get the section number, we
        just use an incrementor

        :param instance: section obj
        """
        self.indexCounter += 1
        return self.indexCounter

    section_number.short_description = 'Section'


    def get_queryset(self, request, obj=None):
        """Description of get_queryset - the query starts out with an 
        empty qeuryset 'prep_id=XXXX' so the initial page is empty 
        and the user is forced to select one and only one animal. 
        The order is descided upon whether the brain was section 
        from left to right, or right to left. This comes
        from the histology table: side_sectioned_first
        
        :param request: http request
        :param obj: section obj
        :return: the queryset ordered correctly
        """
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
        """The edit button is not shown as sections are a view and they can't be changed.

        :param request: http request
        :param obj: the section obj
        :return: False
        """
        return False

    def has_add_permission(self, request, obj=None):
        """The add button is not shown as sections are a view and they can't be added to.

        :param request: http request
        :param obj: the section obj
        :return: False
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """The add button is not shown as sections are a view and they can't be added to.
        
        :param request: http request
        :param obj: the section obj
        :return: False
        """
        return False


@admin.register(admin.models.LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    """This class describes the log objects used during the 
    preprocessing pipeline

    :Inheritance:
        :admin.ModelAdmin: the base Django admin obj
    """
    # to have a date-based drilldown navigation in the admin page
    date_hierarchy = 'action_time'

    # to filter the resultes by users, content types and action flags
    list_filter = ['action_time', 'action_flag']
    search_fields = ['object_repr', 'change_message']
    list_display = ['action_time', 'user', 'content_type', 'action_flag']

    def has_add_permission(self, request):
        """This data is added by the 
        preprocessing pipeline so can't be changed here

        :param request: http request
        :return: False
        """
        return False

    def has_change_permission(self, request, obj=None):
        """This data is added by the preprocessing pipeline so can't be changed here
        
        :param request: http request
        :param obj: the LogEntry obj
        :return: False
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """This data is added by 
        the preprocessing pipeline so can't be deleted here
        
        :param request: http request
        :param obj: the LogEntry obj
        :return: False
        """
        return False

    def has_view_permission(self, request, obj=None):
        """This data can only be viewed by a superuser
        
        :param request: http request
        :param obj: the LogEntry obj
        :return: boolean depending on if the user is a super user or not

        """
        return request.user.is_superuser



admin.site.site_header = 'Active Brain Atlas Admin'
admin.site.site_title = "Active Brain Atlas"
admin.site.index_title = "Welcome to Active Brain Atlas Portal"
admin.site.site_url = "https://github.com/ActiveBrainAtlas2"
