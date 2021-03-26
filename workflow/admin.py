import random
from itertools import zip_longest

from django.contrib import admin
from django.forms import TextInput, Textarea, DateInput, NumberInput, Select
from django.db import models

from plotly.offline import plot
import plotly.graph_objects as go

from neuroglancer.models import UrlModel
from .models import Task, ProgressLookup, TaskView, Log, Journal, Problem, FileLog


class WorkflowAdminModel(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        models.DateTimeField: {'widget': DateInput(attrs={'size':'20'})},
        models.IntegerField: {'widget': NumberInput(attrs={'size':'20'})},
        models.TextField: {'widget': Textarea(attrs={'rows':10, 'cols':100})},
    }

@admin.register(ProgressLookup)
class ProgressLookupAdmin(admin.ModelAdmin):
    list_display = ('description', 'script')
    search_fields = ('description',)
    ordering = ['id']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('prep_id', 'task', 'is_complete')
    search_fields = ('prep__prep_id',)
    ordering = ['prep', 'lookup']
    list_filter = ['created']


    def is_complete(self, instance):
        return instance.completed == 1

    is_complete.boolean = True

    def task(self, instance):
        return instance.lookup.description

    def prep_id(self, instance):
        return instance.prep.prep_id



@admin.register(TaskView)
class TaskViewAdmin(admin.ModelAdmin):
    list_display = ('prep_id', 'percent_complete')
    change_list_template = "admin/task_view.html"
    ordering = ['prep_id']
    readonly_fields = ['prep_id', 'percent_complete']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(TaskViewAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

# add url to view more detail

    def changelist_view(self, request, extra_context=None):
        # Aggregate new subscribers per day
        tasks = TaskView.objects.order_by('prep_id').all()
        lookups = ProgressLookup.objects.order_by('id').all()

        lookup_list = []
        id_list = []
        for i, (look, task) in enumerate(zip_longest(lookups, tasks)):
            descs = look.description
            lookup_list.append(descs)
            id_list.append(i)

        x = []
        y = []
        created = []
        for row in tasks:
            y.append(row.prep_id)
            x.append(row.complete)
            created.append(row.created)

        limit = len(lookup_list)
        get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
        colors = get_colors(len(x))
        fig = go.Figure(data=[go.Bar(x=x, y=y, orientation='h', marker=dict(color=colors), hovertext = created )])
        fig.update_layout(xaxis_showgrid=True, yaxis_showgrid=True, height=600)
        fig.update_xaxes(ticks='outside',tickwidth=2, tickangle=45, tickcolor='crimson', ticklen=10, range=[0,limit])

        fig.update_layout(autosize=True, xaxis=dict(tickmode='array', tickvals=id_list, ticktext=lookup_list),

                          margin=dict(l=20, r=20, t=20, b=280),
                          paper_bgcolor="LightSteelBlue",
                          )
        gantt_div = plot(fig, output_type='div', include_plotlyjs=False)
        # Serialize and attach the workflow data to the template context
        extra_context = extra_context or {"gantt_div": gantt_div, 'title':'Pipeline Progress by Animal'}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)



@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('prep_id', 'level', 'logger', 'msg', 'created')
    ordering = ['prep_id', 'created']
    list_filter = ['created', 'level']
    list_display_links = None
    search_fields = ['prep_id', 'msg']


    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Journal)
class JournalAdmin(WorkflowAdminModel):
    list_display = ('prep_id', 'issue_tag', 'person', 'problem', 'completed', 'link_tag', 'created')
    ordering = ['prep_id', 'created']
    list_filter = ['created', 'completed']
    search_fields = ['prep__prep_id','entry']
    fields = ['prep', 'url', 'section','channel', 'entry', 'fix', 'person', 'problem', 'completed', 'active', 'image','issue_link', 'image_tag']
    readonly_fields = ['image_tag', 'link_tag', 'issue_tag']

    def prep_id(self, instance):
        return instance.prep.prep_id

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        kwargs["widget"] = Select(attrs={'style': 'width: 250px;'})
        if db_field.name == "url":
            kwargs["queryset"] = UrlModel.objects.order_by('comments')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('problem_category', )

@admin.register(FileLog)
class FileLogAdmin(admin.ModelAdmin):
    list_display = ('prep_id', 'filename')
