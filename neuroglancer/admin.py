from django.db import models
import json
from django.conf import settings
from django.contrib import admin, messages
from django.forms import TextInput
from django.urls import reverse, path
from django.utils.html import format_html, escape
from django.template.response import TemplateResponse
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer
from django.utils.safestring import mark_safe
from plotly.offline import plot
import plotly.express as px
from brain.admin import AtlasAdminModel, ExportCsvMixin
from neuroglancer.models import AlignmentScore, \
        AnnotationSession, AnnotationPointArchive, \
        UrlModel,  BrainRegion, Points, \
        PolygonSequence, MarkedCell, StructureCom,CellType
from neuroglancer.dash_view import dash_scatter_view
from neuroglancer.url_filter import UrlFilter
from neuroglancer.AnnotationManager import restore_annotations
from background_task.models import Task
from background_task.models import CompletedTask

def datetime_format(dtime):
    return dtime.strftime("%d %b %Y %H:%M")


@admin.register(AlignmentScore)
class AlignmentScoreAdmin(admin.ModelAdmin):
    """This class provides information for constructing the alignment score graph page."""
    change_list_template = "alignment_score.html"

    def has_add_permission(self, request):
        """Returns false as it is readonly"""
        return False

    def has_change_permission(self, request, obj=None):
        """Returns false as it is readonly"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Returns false as it is readonly"""
        return False


@admin.register(UrlModel)
class UrlModelAdmin(admin.ModelAdmin):
    """This class provides the admin backend to the JSON data produced by Neuroglancer.
    In the original version of Neuroglancer, all the data was stored in the URL, hence
    the name of this class. The name: 'UrlModel' will be changed in future versions."""
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '100'})},
    }
    list_display = ('animal', 'open_neuroglancer', 'open_multiuser',
                    'owner', 'updated')
    ordering = ['-vetted', '-updated']
    readonly_fields = ['pretty_url', 'created', 'user_date', 'updated']
    exclude = ['url']
    list_filter = ['updated', 'created', 'vetted',UrlFilter,]
    search_fields = ['comments']

    def pretty_url(self, instance):
        """Function to display pretty version of the JSON data.
        It uses the pygments library to make the JSON readable.
        
        :param instance: admin obj
        :returns: nicely formatted JSON data that is viewed in the page."""
        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.url, sort_keys=True, indent=2)
        # Truncate the data. Alter as needed
        # response = response[:5000]
        # Get the Pygments formatter
        formatter = HtmlFormatter(style='colorful')
        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)
        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        # Safe the output
        return mark_safe(style + response)

    pretty_url.short_description = 'Formatted URL'

    def open_neuroglancer(self, obj):
        host = "https://webdev.dk.ucsd.edu/preview"
        if settings.DEBUG:
            # stop changing this.
            host = "http://127.0.0.1:8080"

        comments = escape(obj.comments)
        links = f'<a target="_blank" href="{host}?id={obj.id}">{comments}</a>'
        return format_html(links)

    def open_multiuser(self, obj):
        host = "https://activebrainatlas.ucsd.edu/ng_multi"
        if settings.DEBUG:
            host = "http://127.0.0.1:8080"

        comments = "Testing"
        links = f'<a target="_blank" href="{host}?id={obj.id}&amp;multi=1">{comments}</a>'
        return format_html(links)

    open_neuroglancer.short_description = 'Neuroglancer'
    open_neuroglancer.allow_tags = True
    open_multiuser.short_description = 'Multi-User'
    open_multiuser.allow_tags = True

@admin.register(Points)
class PointsAdmin(admin.ModelAdmin):
    """This class may become deprecated, but for now it gets point data
    from the actual JSON and not the 3 new tables we have that contain x,y,z data."""
    list_display = ('animal', 'comments', 'owner','show_points', 'updated')
    ordering = ['-created']
    readonly_fields = ['url', 'created', 'user_date', 'updated']
    search_fields = ['comments']
    list_filter = ['created', 'updated','vetted']

    def created_display(self, obj):
        """Returns a nicely formatted creation date."""
        return datetime_format(obj.created)
    created_display.short_description = 'Created'  

    def get_queryset(self, request):
        """Returns the query set of points where the layer contains annotations"""
        points = Points.objects.filter(url__layers__contains={'type':'annotation'})
        return points

    def show_points(self, obj):
        """Shows the HTML for the link to the graph of data."""
        return format_html(
            '<a href="{}">3D Graph</a>&nbsp; <a href="{}">Data</a>',
            reverse('admin:points-3D-graph', args=[obj.pk]),
            reverse('admin:points-data', args=[obj.pk])
        )

    def get_urls(self):
        """Shows the HTML of the links to go to the graph, and table data."""
        urls = super().get_urls()
        custom_urls = [
            path(r'scatter/<pk>', dash_scatter_view, name="points-2D-graph"),
            path('points-3D-graph/<id>', self.view_points_3Dgraph, name='points-3D-graph'),
            path('points-data/<id>', self.view_points_data, name='points-data'),
        ]
        return custom_urls + urls

    def view_points_3Dgraph(self, request, id, *args, **kwargs):
        """Provides a link to the 3D point graph

        :param request: http request
        :param id:  id of url
        :param args:
        :param kwargs:
        :return: 3dGraph in a django template
        """
        urlModel = UrlModel.objects.get(pk=id)
        df = urlModel.points
        plot_div = "No points available"
        if df is not None and len(df) > 0:
            self.display_point_links = True
            fig = px.scatter_3d(df, x='X', y='Y', z='Section',
                                color='Layer', opacity=0.7)
            fig.update_layout(
                scene=dict(
                    xaxis=dict(nticks=4, range=[20000, 60000], ),
                    yaxis=dict(nticks=4, range=[10000, 30000], ),
                    zaxis=dict(nticks=4, range=[100, 350], ), ),
                width=1200,
                margin=dict(r=0, l=0, b=0, t=0))
            fig.update_traces(marker=dict(size=2),
                              selector=dict(mode='markers'))
            plot_div = plot(fig, output_type='div', include_plotlyjs=False)
        context = dict(
            self.admin_site.each_context(request),
            title=urlModel.comments,
            chart=plot_div
        )
        return TemplateResponse(request, "points_graph.html", context)

    def view_points_data(self, request, id, *args, **kwargs):
        """Provides the HTML link to the table data"""
        urlModel = UrlModel.objects.get(pk=id)
        df = urlModel.points
        result = 'No data'
        display = False
        if df is not None and len(df) > 0:
            display = True
            df = df.sort_values(by=['Layer','Section', 'X', 'Y'])
            result = df.to_html(index=False, classes='table table-striped table-bordered', table_id='tab')
        context = dict(
            self.admin_site.each_context(request),
            title=urlModel.comments,
            chart=result,
            display=display,
            opts=UrlModel._meta,
        )
        return TemplateResponse(request, "points_table.html", context)

    def has_delete_permission(self, request, obj=None):
        """Returns false as the data is readonly"""
        return False

    def has_add_permission(self, request, obj=None):
        """Returns false as the data is readonly"""
        return False

    def has_change_permission(self, request, obj=None):
        """Returns false as the data is readonly"""
        return False


@admin.register(BrainRegion)
class BrainRegionAdmin(AtlasAdminModel, ExportCsvMixin):
    """Class that provides admin capability for managing a region of the brain. This
    was also called a structure."""
    list_display = ('abbreviation', 'description', 'color',
                    'show_hexadecimal', 'active', 'created_display')
    ordering = ['abbreviation']
    readonly_fields = ['created']
    list_filter = ['created', 'active']
    search_fields = ['abbreviation', 'description']

    def created_display(self, obj):
        """Formats the date nicely."""
        return datetime_format(obj.created)
    created_display.short_description = 'Created'

    def show_hexadecimal(self, obj):
        """Formats the hexadecimal nicely."""
        return format_html('<div style="background:{}">{}</div>', obj.hexadecimal, obj.hexadecimal)
    show_hexadecimal.short_description = 'Hexadecimal'

@admin.register(CellType)
class CellTypeAdmin(AtlasAdminModel, ExportCsvMixin):
    list_display = ('cell_type', 'description','active')
    ordering = ['cell_type']
    readonly_fields = ['created']
    list_filter = ['created', 'active']
    search_fields = ['cell_type', 'description']
    def created_display(self, obj):
        return datetime_format(obj.created)
    created_display.short_description = 'Created'    

def make_inactive(modeladmin, request, queryset):
    queryset.update(active=False)
make_inactive.short_description = "Mark selected COMs as inactive"

def make_active(modeladmin, request, queryset):
    queryset.update(active=True)
make_active.short_description = "Mark selected COMs as active"

@admin.register(MarkedCell)
class MarkedCellAdmin(admin.ModelAdmin):
    """This class provides the ability to manage the data entered through Neuroglancer. 
    These are the starter, premotor cells marked by an anatomist or generated through cell detection."""
    list_display = ('animal','annotator','cell_type','brain_region', 'x', 'y', 'z', 'source','created')
    search_fields = ('annotation_session__animal__prep_id','annotation_session__annotator__username','cell_type__cell_type','annotation_session__brain_region__abbreviation', 'x', 'y', 'z', 'source')
    ordering = ('annotation_session__animal__prep_id','annotation_session__annotator__username','cell_type__cell_type','annotation_session__brain_region__abbreviation', 'x', 'y', 'z', 'source')
    list_filter = ['cell_type__cell_type','source']

@admin.register(PolygonSequence)
class PolygonSequenceAdmin(admin.ModelAdmin):
    """This class provides the ability to manage the data entered through Neuroglancer. 
    These are polygons drawn by an anatomist."""
    list_display = ('animal','annotator','created','brain_region', 'source', 'x', 'y', 'z')
    ordering = ('annotation_session__animal__prep_id','annotation_session__annotator__username','annotation_session__brain_region__abbreviation', 'x', 'y', 'z', 'source')
    search_fields = ('annotation_session__animal__prep_id','annotation_session__annotator__username','annotation_session__brain_region__abbreviation', 'source')


@admin.register(StructureCom)
class StructureComAdmin(admin.ModelAdmin):
    """This class provides the ability to manage the data entered through Neuroglancer. 
    These are points are entered by an anatomist and are solely for the center of mass (COM) for a brain region (structure)"""
    list_display = ('animal','annotator','created','brain_region', 'source', 'x', 'y', 'z')
    ordering = ('annotation_session__animal__prep_id','annotation_session__annotator__username','annotation_session__brain_region__abbreviation', 'x', 'y', 'z', 'source')
    search_fields = ('annotation_session__animal__prep_id','annotation_session__annotator__username','annotation_session__brain_region__abbreviation', 'source')

"""
@admin.register(AnnotationPointArchive)
class AnnotationPointArchiveAdmin(admin.ModelAdmin):
    # change_list_template = 'layer_data_group.html'
    list_display = ('annotation_session', 'label', 'x', 'y', 'z')
    ordering = ['label', 'z']
    search_fields = ['label']
"""

@admin.action(description='Restore the selected archive')
def restore_archive(modeladmin, request, queryset):
    """This method will restore data from the annotation_points_archive table to the 
    annotations_points table.
    
    1. Set existing data to inactive (quick)
    2. Move inactive data to archive (select, insert, slow, use background)
    3. Move archived data to existing (select, insert, slow use background)

    :param request: the HTTP request
    :param queryset: the query set used to fetch data
    """
    n = len(queryset)
    if n != 1:
        messages.error(request, 'Check just one archive. You cannot restore more than one archive.')
    else:
        archive = queryset[0]
        restore_annotations(archive.id, archive.animal.prep_id, archive.label)
        messages.info(request, f'The {archive.label} layer for {archive.animal.prep_id} has been restored. ID={archive.id}')
            

@admin.register(AnnotationSession)
class AnnotationSessionAdmin(AtlasAdminModel):
    """Administer the annotation session data."""
    list_display = ['animal', 'annotation_type', 'created','annotator','archive_count']
    ordering = ['animal', 'annotation_type', 'parent', 'created','annotator']
    list_filter = ['animal', 'annotation_type', 'created','annotator']
    search_fields = ['animal', 'annotation_type','annotator']
    actions = [restore_archive]
    
    def archive_count(self, obj):
        """Returns a count of the annotation points per session"""
        count = AnnotationPointArchive.objects.filter(annotation_session=obj).count()
        return count

    archive_count.short_description = "# Points"

admin.site.unregister(Task)
admin.site.unregister(CompletedTask)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """This admin class is for taking care of the tasks associated with the pre-processing pipeline."""
    display_filter = ['task_name']
    search_fields = ['task_name', 'task_params', ]
    list_display = ['task_name', 'run_at', 'priority', 'attempts', 'has_error', 'locked_by', 'locked_by_pid_running', ]

    def has_add_permission(self, request, obj=None):
        """Returns false as this data comes in from the pre-processing pipeline."""
        return False

@admin.register(CompletedTask)
class CompletedTaskAdmin(admin.ModelAdmin):
    """This class is used to admin the completed tasks. These are tasks that are long running
    and take to long for an HTTP request. They get sent to the supervisord daemon to be run
    outside the scope of the HTTP request."""
    display_filter = ['task_name']
    search_fields = ['task_name', 'task_params', ]
    list_display = ['task_name', 'run_at', 'priority', 'attempts', 'has_error', 'locked_by', 'locked_by_pid_running', ]

    def has_add_permission(self, request):
        """Returns false as it is added by another process."""
        return False

    def has_change_permission(self, request, obj=None):
        """Returns false as it is added by another process."""
        return False
