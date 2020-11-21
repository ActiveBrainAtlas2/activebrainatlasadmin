import json

from django.contrib import admin
from django.forms import TextInput, ChoiceField
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.utils.html import format_html, escape
from django.template.response import TemplateResponse
from django import forms
import neuroglancer.dash_apps

from neuroglancer.models import UrlModel, Structure, Points, CenterOfMass
import plotly.express as px
from plotly.offline import plot
from django.db import models
from neuroglancer.graphs import create_2Dgraph
from neuroglancer.dash_view import dash_scatter_view

# Register your models here.


@admin.register(UrlModel)
class UrlModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
    }

    list_display = ('animal', 'open_neuroglancer','person', 'updated', 'vetted')
    ordering = ['-vetted', '-updated']
    readonly_fields = ['url', 'created', 'user_date', 'updated']
    list_filter = ['created', 'vetted']
    search_fields = ['url', 'comments']


    def open_neuroglancer(self, obj):

        return format_html('<a target="_blank" href="https://activebrainatlas.ucsd.edu/ng/?id={}&amp;#!{}">{}</a>',
                           obj.id, escape(obj.url), escape(obj.comments))


    open_neuroglancer.short_description = 'Neuroglancer'
    open_neuroglancer.allow_tags = True


@admin.register(Points)
class PointsAdmin(admin.ModelAdmin):
    list_display = ('animal', 'comments', 'person','show_points', 'created', 'updated')
    ordering = ['-created']
    readonly_fields = ['url', 'created', 'user_date', 'updated']
    search_fields = ['comments']

    def get_queryset(self, request):
        points = Points.objects.filter(url__contains='annotations')
        points = points.filter(url__contains='point')
        return points


    def show_points(self, obj):
        display_2dgraph = obj.point_count

        return format_html(
            '<a href="{}">3D Graph</a>&nbsp; <a href="{}">Data</a> <a href="{}" style="{}";>2D Graph</a>&nbsp; ',
            reverse('admin:points-3D-graph', args=[obj.pk]),
            reverse('admin:points-data', args=[obj.pk]),
            reverse('admin:points-2D-graph', args=[obj.pk]),
            display_2dgraph
        )


    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(r'scatter/<pk>', dash_scatter_view, name="points-2D-graph"),
            path('points-3D-graph/<id>', self.view_points_3Dgraph, name='points-3D-graph'),
            path('points-data/<id>', self.view_points_data, name='points-data'),
        ]
        return custom_urls + urls


    def view_points_3Dgraph(self, request, id, *args, **kwargs):
        """
        3d graph
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
            display=display
        )
        return TemplateResponse(request, "points_table.html", context)

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'description','color','show_hexadecimal','active','created')
    ordering = ['abbreviation']
    readonly_fields = ['created']
    list_filter = ['created', 'active']
    #list_filter = (VettedFilter,)
    search_fields = ['abbreviation', 'description']


    def show_hexadecimal(self, obj):
        return format_html('<div style="background:{}">{}</div>',obj.hexadecimal,obj.hexadecimal)

    show_hexadecimal.short_description = 'Hexadecimal'


@admin.register(CenterOfMass)
class CenterOfMassAdmin(admin.ModelAdmin):
    list_display = ('prep_id', 'structure','x','y', 'section', 'active','created')
    ordering = ['prep_id', 'structure']
    readonly_fields = ['created']
    list_filter = ['created', 'active']
    search_fields = ('prep__prep_id',)


