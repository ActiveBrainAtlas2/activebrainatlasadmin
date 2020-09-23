from django.contrib import admin
from django.forms import TextInput
from django.urls import reverse, path
from django.utils.html import format_html, escape
from django.template.response import TemplateResponse
from neuroglancer.models import UrlModel, Structure
import plotly.express as px
from plotly.offline import plot
import plotly.graph_objects as go
from django.db import models


# Register your models here.


@admin.register(UrlModel)
class UrlModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
    }

    list_display = ('animal', 'open_neuroglancer','vetted','person','show_points', 'created')
    ordering = ['-created']
    readonly_fields = ['url', 'created', 'user_date']
    list_filter = ['created', 'vetted']
    search_fields = ['url', 'comments']


    def open_neuroglancer(self, obj):
        return format_html('<a target="_blank" href="https://activebrainatlas.ucsd.edu/ng/?id={}&amp;#!{}">{}</a>',
                           obj.id, escape(obj.url), escape(obj.comments))

    def show_points(self, obj):
        return format_html(
            '<a href="{}">Graph</a>&nbsp; <a href="{}">Data</a>',
            reverse('admin:points-graph', args=[obj.pk]),
            reverse('admin:points-data', args=[obj.pk])
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            # path('<prep_id>', self.admin_site.admin_view(self.process_section),  name='account-deposit',
            path('points-graph/<id>', self.view_points_graph, name='points-graph'),
            path('points-data/<id>', self.view_points_data, name='points-data'),
        ]
        return custom_urls + urls

    def view_points_graph(self, request, id, *args, **kwargs):
        urlModel = UrlModel.objects.get(pk=id)
        df = urlModel.points
        plot_div = "No points available"
        if df is not None and len(df) > 0:
            fig = px.scatter_3d(df, x='X', y='Y', z='Section',
                                color='Layer', opacity=0.7)
            fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))

            plot_div = plot(fig, output_type='div', include_plotlyjs=False)


        context = dict(
            self.admin_site.each_context(request),
            title=urlModel.comments,
            chart=plot_div
        )
        return TemplateResponse(request, "points.html", context)

    def view_points_data(self, request, id, *args, **kwargs):
        urlModel = UrlModel.objects.get(pk=id)
        df = urlModel.points
        plot_div = "No points available"
        if df is not None and len(df) > 0:
            df = df.sort_values(by=['Layer','Section', 'X', 'Y'])
            fig = go.Figure(data=[go.Table(
                header=dict(values=list(df.columns),
                            fill_color='paleturquoise',
                            align='left'),
                cells=dict(values=[df.Layer, df.X, df.Y, df.Section],
                           fill_color='lavender',
                           align='left'))
            ])

            plot_div = plot(fig, output_type='div', include_plotlyjs=False)


        context = dict(
            self.admin_site.each_context(request),
            title=urlModel.comments,
            chart=plot_div
        )
        return TemplateResponse(request, "points.html", context)


    open_neuroglancer.short_description = 'Neuroglancer'
    open_neuroglancer.allow_tags = True


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ('abbreviation', 'description','color','show_hexadecimal','active','paired','created')
    ordering = ['abbreviation']
    readonly_fields = ['created']
    list_filter = ['created', 'active']
    search_fields = ['abbreviation', 'description']


    def show_hexadecimal(self, obj):
        return format_html('<div style="background:{}">{}</div>',obj.hexadecimal,obj.hexadecimal)

    show_hexadecimal.short_description = 'Hexadecimal'
