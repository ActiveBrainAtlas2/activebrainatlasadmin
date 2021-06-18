import random

from django.contrib import admin
from django.forms import TextInput, Textarea, DateInput, NumberInput, Select
from django.db import models
from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count

from plotly.offline import plot
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from neuroglancer.models import UrlModel, LayerData
from neuroglancer.atlas import get_atlas_centers,get_centers_dict
from brain.models import Animal
from workflow.models import Task, ProgressLookup, TaskView, Log, Journal, Problem, FileLog

from workflow.forms import PipelineForm
from celery import chain
from workflow.tasks import setup, make_meta, make_tifs, make_scenes
import plotly.express as px
import numpy as np
import pandas as pd
from timeit import default_timer as timer
# from test.get_data_from_histogram import prepare_table_for_plot

class WorkflowAdminModel(admin.ModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        models.DateTimeField: {'widget': DateInput(attrs={'size':'20'})},
        models.IntegerField: {'widget': NumberInput(attrs={'size':'20'})},
        models.TextField: {'widget': Textarea(attrs={'rows':10, 'cols':100})},
    }

@admin.register(ProgressLookup)
class ProgressLookupAdmin(admin.ModelAdmin):
    list_display = ('description', 'script', 'action', 'channel', 'downsample')
    search_fields = ('description',)
    ordering = ['description']


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

    def view_pipeline(self, request):
        celery_task_ids = {}
        animal = None
        title = 'Active Brain Atlas Pipeline'
        
        if request.method == 'POST':
            form = PipelineForm(request.POST)


            if form.is_valid():
                animal = form.cleaned_data['animal']
                print(f'type of animal is {type(animal)}')
                # do celery stuff here.
                animal = animal.prep_id
                
                result = chain(
                    setup.si(animal),
                    make_meta.si(animal),
                    make_tifs.si(animal, 1, 3),
                    make_scenes.si(animal, 3)
                ).apply_async()
                scene_id =  result.id
                meta_id = result.parent.id
                tif_id =  result.parent.parent.id
                setup_id = result.parent.parent.parent.id                
                ids = [setup_id, tif_id, meta_id, scene_id]
                
                #result = setup.delay(animal)
                #ids = [result.id]
                print(result.status, ids)
                for i, task_id in enumerate(ids):
                    celery_task_ids[i] = task_id
                celery_task_ids = celery_task_ids
                title = f'Active Brain Atlas {animal} Pipeline'
                form = None

        else:
            form = PipelineForm()
        

        context = dict(
            self.admin_site.each_context(request),
            title = title,
            form = form,
            animal = animal,
            celery_task_ids = celery_task_ids
        )
        return TemplateResponse(request, "pipeline.html", context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('pipeline/', self.admin_site.admin_view(self.view_pipeline))
        ]
        return my_urls + urls
       

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


    def changelist_view(self, request, extra_context=None):
        counts = Task.objects.all().filter(lookup__channel__in=[0,1]).filter(lookup__downsample=False)\
        .filter(prep__active=True)\
        .values('prep_id').annotate(total=Count('prep_id')).order_by('prep_id')
        animals = Animal.objects.filter(active=True).order_by('prep_id').all()
        lookups = ProgressLookup.objects.filter(channel__in=[0,1]).filter(downsample=False).order_by('id').all()

        al = []
        x = [] 
        i = 0
        for animal in animals:
            if animal.aliases_1 is None:
                continue
            al.append(str(animal.prep_id + '-' + animal.aliases_1))
            x.append(counts[i]['total'])
            i += 1

        lookup_list = []
        id_list = []
        for i, lookup in enumerate(lookups):
            id_list.append(i)
            lookup_list.append(lookup.action)
        limit = len(lookup_list)
        colors = [x*19 for x in range(len(x))]
        marker={'color': colors, 'colorscale': 'Viridis'}
        fig = go.Figure(data=[go.Bar(x=x, y=al, orientation='h', marker=marker )])
        fig.update_layout(xaxis_showgrid=True, yaxis_showgrid=True, height=600)
        fig.update_xaxes(ticks='outside',tickwidth=2, tickangle=45, tickcolor='crimson', ticklen=10, range=[0,limit-1])
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
    list_display = ('problem_category', 'active', 'created')

@admin.register(FileLog)
class FileLogAdmin(admin.ModelAdmin):
    list_display = ('prep_id', 'filename')

# my dummy model
class DummyModel(models.Model):
    prep_id = models.CharField(primary_key=True, max_length=20)
    percent_complete = models.DecimalField(max_digits=6, decimal_places=2)
    complete = models.IntegerField()
    created = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'task_view'
        verbose_name = 'center of mass histograms'
        verbose_name_plural = 'center of mass histograms'

    def __str__(self):
        return u'{}'.format(self.prep_id)


@admin.register(DummyModel)
class DummyModelAdmin(admin.ModelAdmin):
    change_list_template = "alignment.html"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


    def changelist_view(self, request, extra_context=None):
        start = timer()
        #brains_to_examine = ['DK39', 'DK41', 'DK43', 'DK52', 'DK54', 'DK55']
        brains = list(LayerData.objects.filter(active=True)\
            .filter(input_type__input_type__in=['manual'])\
            .filter(layer='COM')\
            .filter(active=True)\
            .exclude(prep_id='Atlas')\
            .values_list('prep_id', flat=True).distinct().order_by('prep_id'))
        print(brains)
        PERSON_ID_BILLI = 28
        INPUT_TYPE_ALIGNED = 4
        INPUT_TYPE_CORRECTED = 2
        atlas_coms = get_atlas_centers()
        common_structures = get_common_structure(brains)

        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=("Rigid Alignment Error", "Rigid Alignment Error After Correction", "Rough Alignment Error"))
        df1 = prepare_table_for_plot(atlas_coms, common_structures,
            brains,
            person_id=PERSON_ID_BILLI,
            input_type_id=INPUT_TYPE_ALIGNED,)
        df2 = prepare_table_for_plot(atlas_coms, common_structures,
            brains,
            person_id=PERSON_ID_BILLI,
            input_type_id=INPUT_TYPE_CORRECTED,)
        df3 = prepare_table_for_plot(atlas_coms, common_structures,
            brains,
            person_id=1,
            input_type_id=INPUT_TYPE_ALIGNED,)
        add_trace(df1,fig,1)
        add_trace(df2,fig,2)
        add_trace(df3,fig,3)
        fig.update_layout(
            autosize=False,
            height=1000,
            margin=dict(l=50, r=50, b=100, t=100, pad=4),
            paper_bgcolor="LightSteelBlue",
        )  
        gantt_div = plot(fig, output_type='div', include_plotlyjs=False)
        # Serialize and attach the workflow data to the template context
        title = 'Rigid Alignment Error for ' + ", ".join(brains)
        extra_context = extra_context or {"gantt_div": gantt_div, 'title':title}

        # Call the superclass changelist_view to render the page
        end = timer()
        print(f'change list view took {end - start} seconds')
        return super().changelist_view(request, extra_context=extra_context)



def get_common_structure(brains):
    start = timer()
    common_structures = set()
    for brain in brains:
        common_structures = common_structures | set(get_centers_dict(brain).keys())
    common_structures = list(sorted(common_structures))
    end = timer()
    print(f'get common structures took {end - start} seconds')
    return common_structures


def get_brain_coms(brains, person_id, input_type_id):
    start = timer()
    brain_coms = {}
    for brain in brains:
        brain_coms[brain] = get_centers_dict(
            prep_id = brain,
            person_id=person_id,
            input_type_id=input_type_id
        )
    end = timer()
    print(f'get brain coms took {end - start} seconds')
    return brain_coms

def prepare_table_for_plot(atlas_coms, common_structures, brains, person_id, input_type_id):
    start = timer()
    global dx,dy,dz,dist,structurei
    brain_coms = get_brain_coms(brains, input_type_id = input_type_id, person_id = person_id )
    df = pd.DataFrame()
    for brain in brain_coms.keys():
        offset = [brain_coms[brain][s] - atlas_coms[s]
                  if s in brain_coms[brain] else [np.nan, np.nan, np.nan]
                  for s in common_structures]
        offset = np.array(offset)
        scale = np.array([10, 10, 20])
        dx, dy, dz = (offset * scale).T
        dist = np.sqrt(dx * dx + dy * dy + dz * dz)
        df_brain = pd.DataFrame()
        data = {}
        data['structure'] = [structurei + '_dx' for structurei in common_structures]
        data['value'] = dx
        data['type'] = 'dx'
        df_brain = df_brain.append(pd.DataFrame(data), ignore_index=True)

        data = {}
        data['structure'] = [structurei + '_dy' for structurei in common_structures]
        data['value'] = dy
        data['type'] = 'dy'
        df_brain = df_brain.append(pd.DataFrame(data), ignore_index=True)

        data = {}
        data['structure'] = [structurei + '_dz' for structurei in common_structures]
        data['value'] = dz
        data['type'] = 'dz'
        df_brain = df_brain.append(pd.DataFrame(data), ignore_index=True)

        data = {}
        data['structure'] = [structurei + '_dist' for structurei in common_structures]
        data['value'] = dist
        data['type'] = 'dist'
        df_brain = df_brain.append(pd.DataFrame(data), ignore_index=True)

        df_brain['brain'] = brain
        df = df.append(df_brain, ignore_index=True)
    end = timer()
    print(f'prepare table for plot took {end - start} seconds')
    return df

def add_trace(df,fig,rowi):
    start = timer()
    colors = ["#ee6352","#08b2e3","#484d6d","#57a773"]
    colori = 0
    for row_type in ['dx','dy','dz','dist']:
        rows_of_type = df[df.type==row_type]
        fig.append_trace(
            go.Scatter(x=rows_of_type['structure'],
                y=rows_of_type['value'],mode='markers', 
                marker_color = colors[colori],
                name = row_type,
                text=rows_of_type['brain']),
                row = rowi,col=1
                )
        colori+=1
    end = timer()
    print(f'add_trace took {end - start} seconds')