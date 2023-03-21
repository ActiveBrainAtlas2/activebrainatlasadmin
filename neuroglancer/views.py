"""This is the module that the user will use to connect to the database.
This can be defined in either a web page or in a REST API call. This module
is the 'V' in the MVC framework for the Neuroglancer app
portion of the portal.
"""

import decimal
from django.db.models import Count
from rest_framework import viewsets, views, permissions, status
from django.db.models import Q
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination

from neuroglancer.annotation_controller import create_polygons
from neuroglancer.annotation_base import AnnotationBase
from neuroglancer.annotation_layer import random_string, create_point_annotation
from neuroglancer.annotation_manager import DEBUG
from neuroglancer.atlas import align_atlas, get_scales, make_ontology_graph_CCFv3, make_ontology_graph_pma
from neuroglancer.create_state_views import create_layer, create_neuroglancer_model, prepare_bottom_attributes, prepare_top_attributes
from neuroglancer.models import UNMARKED, AnnotationSession, MarkedCell, NeuroglancerView, PolygonSequence, \
    NeuroglancerState, BrainRegion, StructureCom, CellType, MouselightNeuron,ViralTracingLayer 
from neuroglancer.serializers import AnnotationSerializer, ComListSerializer, \
    MarkedCellListSerializer, NeuroglancerViewSerializer, NeuroglancerGroupViewSerializer, PolygonListSerializer, \
    PolygonSerializer, RotationSerializer, NeuroglancerStateSerializer, \
    NeuronSerializer, AnatomicalRegionSerializer, \
    ViralTracingSerializer 
from neuroglancer.tasks import background_archive_and_insert_annotations, \
    nobackground_archive_and_insert_annotations
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
from subprocess import check_output
import os
from time import sleep


def apply_scales_to_annotation_rows(rows, prep_id):
    """To fetch the scan resolution of an animal from the database and apply it to a 
    list of annotation rows

    :param rows: list of query result from either the StructureCom, MarkedCell, 
        or PolygonSequence table.
    :param prep_id: string animal id
    """

    scale_xy, z_scale = get_scales(prep_id)
    for row in rows:
        row.x = row.x / scale_xy
        row.y = row.y / scale_xy
        row.z = row.z / z_scale + decimal.Decimal(0.5)



class GetVolume(AnnotationBase, views.APIView):
    """A view that returns the volume annotation for a session in neuroglancer json format
    """

    def get(self, request, session_id, format=None):
        try:
            session = AnnotationSession.objects.get(pk=session_id)
            rows = PolygonSequence.objects.filter(
                annotation_session__pk=session_id)
        except:
            print('bad query')
        apply_scales_to_annotation_rows(rows, session.animal.prep_id)
        polygon_data = self.create_polygon_and_volume_uuids(rows)
        polygons = create_polygons(
            polygon_data, description=session.brain_region.abbreviation)
        serializer = PolygonSerializer(polygons, many=True)
        return Response(serializer.data)

    def create_polygon_and_volume_uuids(self, rows):
        polygon_index_to_id = {}
        volume_id = random_string()
        polygon_data = []
        for i in rows:
            if not i.polygon_index in polygon_index_to_id:
                polygon_index_to_id[i.polygon_index] = random_string()
            i.polygon_id = polygon_index_to_id[i.polygon_index]
            i.volume_id = volume_id
            polygon_data.append(i)
        return polygon_data


class GetCOM(AnnotationBase, views.APIView):
    """A view that returns the COM for a perticular annotator in neuroglancer json format
    """

    def get(self, request, prep_id, annotator_id, source, format=None):
        self.set_animal_from_id(prep_id)
        self.set_annotator_from_id(annotator_id)
        try:
            rows = StructureCom.objects.filter(annotation_session__animal=self.animal)\
                .filter(source=source).filter(annotation_session__annotator=self.annotator)
        except:
            print('bad query')
        apply_scales_to_annotation_rows(rows, self.animal.prep_id)
        data = []
        for row in rows:
            coordinates = [int(round(row.x)), int(round(row.y)), row.z]
            description = row.annotation_session.brain_region.abbreviation
            point_annotation = create_point_annotation(
                coordinates, description, type='com')
            data.append(point_annotation)
        serializer = AnnotationSerializer(data, many=True)
        return Response(serializer.data)


class GetMarkedCell(AnnotationBase, views.APIView):
    """A view that returns the marked cells for a specific annotation session in neuroglancer json format.
    """

    def get(self, request, session_id, format=None):
        try:
            session = AnnotationSession.objects.get(pk=session_id)
        except:
            return Response({"Error": "Record does not exist"}, status=status.HTTP_404_NOT_FOUND)
        rows = MarkedCell.objects.filter(annotation_session__pk=session_id)
        apply_scales_to_annotation_rows(rows, session.animal.prep_id)
        data = []
        for row in rows:
            coordinates = [int(round(row.x)), int(round(row.y)), row.z]
            description = row.source
            if row.source == 'HUMAN_POSITIVE':
                description = 'positive'
            elif row.source == 'HUMAN_NEGATIVE':
                description = 'negative'
            elif row.source == 'MACHINE_SURE':
                description = 'machine_sure'
            elif row.source == 'MACHINE_UNSURE':
                description = 'machine_unsure'
            elif row.source == UNMARKED:
                description = 'unmarked'
            else:
                return Response({"Error": "Source is not correct on annotation session"}, status=status.HTTP_404_NOT_FOUND)
                
             
            point_annotation = create_point_annotation(coordinates, description, type='cell')
            point_annotation['category'] = row.cell_type.cell_type
            data.append(point_annotation)
        serializer = AnnotationSerializer(data, many=True)
        return Response(serializer.data)


class GetComList(views.APIView):
    """A view that returns a list of available COMs.
    """

    def get(self, request, format=None):
        """
        This will get the layers of COMs for the dropdown menu
        """
        data = []
        coms = StructureCom.objects.order_by('annotation_session__animal__prep_id', 
            'annotation_session__annotator__username')\
            .values('annotation_session__animal__prep_id', 'annotation_session__annotator__username', 
            'annotation_session__annotator__id', 'source')\
            .annotate(Count("id"))
        for com in coms:
            data.append({
                "prep_id": com['annotation_session__animal__prep_id'],
                "annotator": com['annotation_session__annotator__username'],
                "annotator_id": com['annotation_session__annotator__id'],
                "source": com['source'],
                "count": com['id__count']
            })
        serializer = ComListSerializer(data, many=True)
        return Response(serializer.data)


class GetPolygonList(views.APIView):
    """A view that returns a list of available brain region volumes.
    """

    def get(self, request, format=None):
        """
        This will get the layer_data
        """
        data = []
        rows = AnnotationSession.objects.filter(
            active=True).filter(annotation_type='POLYGON_SEQUENCE').all()
        for row in rows:
            data.append({
                'session_id': row.id,
                "prep_id": row.animal.prep_id,
                "annotator": row.annotator.username,
                "brain_region": row.brain_region.abbreviation,
                "source": 'NA'
            })
        serializer = PolygonListSerializer(data, many=True)
        return Response(serializer.data)


class GetMarkedCellList(views.APIView):
    """A view that returns a list of available marked cell annotations.
    """

    def get(self, request, format=None):
        """
        This will get the layer_data for the marked cell requested
        """
        data = []
        rows = MarkedCell.objects.filter(annotation_session__active=True)\
            .order_by('annotation_session__animal', 
            'annotation_session__annotator__username')\
            .values('annotation_session__id',
            'annotation_session__animal', 
            'annotation_session__annotator__username',
            'source',
            'cell_type__cell_type',
            'cell_type__id',
            'annotation_session__brain_region__abbreviation',
            'annotation_session__brain_region__id',
            )\
            .distinct()

        for row in rows:
            data.append({
                'session_id': row['annotation_session__id'],
                'prep_id': row['annotation_session__animal'],
                'annotator': row['annotation_session__annotator__username'],
                'source': row['source'],
                'cell_type': row['cell_type__cell_type'],
                'cell_type_id': row['cell_type__id'],
                'structure': row['annotation_session__brain_region__abbreviation'],
                'structure_id': row['annotation_session__brain_region__id'],
            })
        serializer = MarkedCellListSerializer(data, many=True)
        return Response(serializer.data)



class Rotation(views.APIView):
    """A view that returns the transformation from the atlas to the image stack of one 
    particular brain.
    """

    def get(self, request, prep_id, annotator_id, source, reverse=0, reference_scales='None', format=None):
        data = {}
        R, t = align_atlas(prep_id, annotator_id, source,
                           reverse=reverse, reference_scales=eval(reference_scales))
        data['rotation'] = R.tolist()
        data['translation'] = t.tolist()
        return JsonResponse(data)


class Rotations(views.APIView):
    """A view that returns the available set of rotations.
    """

    def get(self, request, format=None):
        data = []
        coms = StructureCom.objects.order_by('annotation_session')\
            .values('annotation_session__animal__prep_id', 'label', 'source').distinct()
        for com in coms:
            data.append({
                "prep_id": com['annotation_session__animal__prep_id'],
                "label": com['label'],
                "source": com['source'],
            })
        serializer = RotationSerializer(data, many=True)
        return Response(serializer.data)


class LandmarkList(views.APIView):
    """A view that returns a list of active brain regions in the structures table.
    """

    def get(self, request, format=None):

        list_of_landmarks = BrainRegion.objects.all().filter(active=True).all()
        list_of_landmarks = [i.abbreviation for i in list_of_landmarks]
        data = {}
        data['land_marks'] = list_of_landmarks
        return JsonResponse(data)


class ContoursToVolume(views.APIView):
    """Method to run slurm to create a 3D volume
    """
    
    def get(self, request, url_id, volume_id):
        command = ["sbatch", os.path.abspath('./slurm_scripts/contour_to_volume'), str(url_id),volume_id]
        print(command)
        out = check_output(command)
        start_id = out.find(b'job')+4
        job_id = int(out[start_id:-1])
        output_file = f'/opt/slurm/output/slurm_{job_id}.out'
        error_file = f'/opt/slurm/output/slurm_{job_id}.err'
        while not os.path.exists(output_file):
            sleep(1)
            print(f'waiting for job {job_id} to finish')
        print('finished')
        text_file = open(output_file, "r")
        data = text_file.read()
        text_file.close()
        url = data.split('\n')[-1]
        folder_name = url.split('/')[-1]
        return JsonResponse({'url': url, 'name': folder_name})

class SaveAnnotation(views.APIView):
    """A view that saves all the annotation in one annotation layer of a specific row in the neuroglancer url table
    There are two methods to save the data, one is in the background and the other is the default way without
    using the background process. We use the background task in production as the method can take a long time
    to complete.
    """
    
    def get(self, request, neuroglancer_state_id, annotation_layer_name):
        neuroglancerState = NeuroglancerState.objects.get(pk=neuroglancer_state_id)
        state_json = neuroglancerState.neuroglancer_state
        layers = state_json['layers']
        found = False
        for layeri in layers:
            if layeri['type'] == 'annotation' and layeri['name'] == annotation_layer_name:

                if DEBUG:
                    nobackground_archive_and_insert_annotations(layeri, neuroglancer_state_id)
                else:
                    background_archive_and_insert_annotations(layeri, neuroglancer_state_id)
                    
                found = True

        if found:
            return Response('success')
        else:
            return Response(f'layer not found {(annotation_layer_name)}')


class GetCellTypes(views.APIView):
    """View that returns a list of cell types
    """

    def get(self, request, format=None):
        data = {}
        cell_types = CellType.objects.filter(active=True).all()
        data['cell_type'] = [i.cell_type for i in cell_types]
        return JsonResponse(data)

##### imported from brainsharer mouselight code

class MouseLightNeuron(views.APIView):
    """
    Fetch MouseLight neurons meeting filter criteria 
    url is of the the form
    mlneurons/<str:atlas_name>/<str:brain_region1>/<str:filter_type1>/<str:operator_type1>/<int:thresh1>/<str:filter_type2>/<str:operator_type2>/<int:thresh2>
    Where:
    - atlas_name     <str> : required, either "ccfv3_25um" or "pma_20um"
    - brain_region1  <str> : required, e.g. "Cerebellum"
    - filter_type1   <str> : optional, e.g. "soma", "axon_endpoints", ...
    - operator_type1 <str> : optional, e.g. "gte" -> "greater than or equal to"
    - thresh1        <int> : optional, e.g. 2 
    - brain_region2  <str> : optional, e.g. "Thalamus"
    - filter_type2   <str> : optional, e.g. "dendritic_branchpoints"
    - operator_type2 <str> : optional, e.g. "eq" -> "exactly equal to"
    - thresh2        <int> : optional, e.g. 5
    """

    """
    Fetch MouseLight neurons meeting filter criteria 
    url is of the the form
    mlneurons/<str:atlas_name>/<str:neuron_parts_boolstr>/<str:brain_region1>/<str:filter_type1>/<str:operator_type1>/<int:thresh1>/<str:filter_type2>/<str:operator_type2>/<int:thresh2>
    Where:
        atlas_name               <str> : required, either "ccfv3_25um" or "pma_20um"
        neuron_parts_boolstr     <str> : required, e.g. "true-true-false" denotes whether to fetch somata, axons and dendrites, respectively
        brain_region1            <str> : required, e.g. "Cerebellum"
        filter_type1             <str> : optional, e.g. "soma", "axon_endpoints", ...
        operator_type1           <str> : optional, e.g. "gte" -> "greater than or equal to"
        thresh1                  <int> : optional, e.g. 2 
        brain_region2            <str> : optional, e.g. "Thalamus"
        filter_type2             <str> : optional, e.g. "dendritic_branchpoints"
        operator_type2           <str> : optional, e.g. "eq" -> "exactly equal to"
        thresh2                  <int> : optional, e.g. 5
    """

    def get(self, request, atlas_name, neuron_parts_boolstr, brain_region1, 
        filter_type1='soma', operator_type1=None, thresh1=None,
        brain_region2=None, filter_type2=None, operator_type2=None, thresh2=None):
        
        print(atlas_name,brain_region1,filter_type1,
            operator_type1,thresh1,brain_region2,
            filter_type2,operator_type2,thresh2)
        
        if atlas_name == 'ccfv3_25um':
            ontology_graph = make_ontology_graph_CCFv3()
        elif atlas_name == 'pma_20um':
            ontology_graph = make_ontology_graph_pma()
        
        # filter to only get neurons in this atlas
        rows = MouselightNeuron.objects.filter(annotation_space__exact=atlas_name)
        all_ids_thisatlas = [x for x in rows.values_list('id',flat=True)]
        # Filter #1, required
        brain_region_id1 = ontology_graph.get_id(brain_region1)
        if filter_type1 == 'soma':
            # Figure out all progeny of this region since neuron could be in this shell or any child
            progeny = ontology_graph.get_progeny(brain_region1)
            progeny_ids = [ontology_graph.get_id(prog) for prog in progeny]
            ids_tosearch = [brain_region_id1] + progeny_ids
            rows = rows.filter(soma_atlas_id__in=ids_tosearch)
        else:
            filter_name1 = f'{filter_type1}_dict__count_{brain_region_id1}__{operator_type1}'
            filter1 = Q(**{filter_name1:thresh1})
            if operator_type1 in ['gte','lte','exact'] and thresh1 == 0:
                filter_name1_nullcheck = f'{filter_type1}_dict__count_{brain_region_id1}__isnull'
                filter1_nullcheck = Q(**{filter_name1_nullcheck:True})
                rows = rows.filter(filter1 | filter1_nullcheck)
            else:
                rows = rows.filter(filter1)
        # Filter #2, optional
        if filter_type2:
            brain_region_id2 = ontology_graph.get_id(brain_region2)
            if filter_type2 == 'soma':
                # Figure out all progeny of this region since neuron could be in this shell or any child
                progeny = ontology_graph.get_progeny(brain_region1)
                progeny_ids = [ontology_graph.get_id(prog) for prog in progeny]
                ids_tosearch = [brain_region_id2] + progeny_ids
                rows = rows.filter(soma_atlas_id__in=ids_tosearch)
            else:
                filter_name2 = f'{filter_type2}_dict__count_{brain_region_id2}__{operator_type2}'
                filter2 = Q(**{filter_name2:thresh2})
                if operator_type2 in ['gte','lte','exact'] and thresh2 == 0:
                    filter_name2_nullcheck = f'{filter_type2}_dict__count_{brain_region_id2}__isnull'
                    filter2_nullcheck = Q(**{filter_name2_nullcheck:True})
                    rows = rows.filter(filter2 | filter2_nullcheck)
                else:
                    rows = rows.filter(filter2)

        neuron_indices = [all_ids_thisatlas.index(ID) for ID in rows.values_list('id',flat=True)]
        # Only add neuron parts we want
        # The "id" in the database describes the neuron id
        # Each neuron has a different skeleton for its soma, axon and dendrite
        # and we can choose which of them to fetch and display in neuroglancer
        # id itself corresponds to the soma  
        # id + 1 corresponds to the axon 
        # id + 2 corresponds to the dendrite
        somata_boolstr, axons_boolstr, dendrites_boolstr = neuron_parts_boolstr.split('-')
        neuron_parts_indices = []
        if somata_boolstr == 'true':
            neuron_parts_indices.append(0) 
        if axons_boolstr == 'true':
            neuron_parts_indices.append(1)
        if dendrites_boolstr == 'true':
            neuron_parts_indices.append(2)
        # make the list of skeleton ids to get based on our database ids as well as 
        # which parts of the neurons we were asked to get
        skeleton_segment_ids = [ix*3+x for ix in neuron_indices for x in neuron_parts_indices]
        serializer = NeuronSerializer({'segmentId':skeleton_segment_ids})
        return Response(serializer.data)

class AnatomicalRegions(views.APIView):
    """
    Fetch the complete list of anatomical brain regions
    url is of the the form
    /anatomicalregions/atlasName
    """
    def get(self, request, atlas_name):
        if atlas_name == 'ccfv3_25um':
            ontology_graph = make_ontology_graph_CCFv3()
        elif atlas_name == 'pma_20um':
            ontology_graph = make_ontology_graph_pma()
        segment_names = list(ontology_graph.graph.keys())
        serializer = AnatomicalRegionSerializer({'segment_names':segment_names})
        return Response(serializer.data)

class TracingAnnotation(views.APIView):
    """Fetch Viral tracing datasets meeting filter criteria 
    url is of the the form
    tracing_annotations/<str:virus_timepoint>/<str:primary_inj_site>
    Where:
    - virus_timepoint   <str> : required, "HSV-H129_Disynaptic", "HSV-H129_Trisynaptic" or "PRV_Disynaptic"
    - primary_inj_site  <str> : required, e.g. "Lob. I-V" 
    """
    def get(self, request, virus_timepoint, primary_inj_site):

        virus,timepoint = virus_timepoint.split("_")

        if primary_inj_site == 'All sites':
            rows = ViralTracingLayer.objects.filter(
                virus=virus,
                timepoint=timepoint)
        else:
            rows = ViralTracingLayer.objects.filter(
                virus=virus,
                timepoint=timepoint,
                primary_inj_site=primary_inj_site)

        brain_names = rows.values_list('brain_name',flat=True)
        brain_urls = [f'https://lightsheetatlas.pni.princeton.edu/public/tracing/{virus_timepoint}/{brain_name}_eroded_cells_no_cerebellum' \
            for brain_name in brain_names]
        
        # Make a dict to map inputs we receive to what the db fields expect
        primary_inj_site_dict = {
            "Lob. I-V":"lob_i_v",
            "Lob. VI, VII":"lob_vi_vii",
            "Lob. VIII-X":"lob_viii_x",
            "Simplex":"simplex",
            "Crus I":"crusi",
            "Crus II":"crusii",
            "PM, CP":"pm_cp",
            "All sites":"all"}
        
        primary_inj_site_fieldname = primary_inj_site_dict[primary_inj_site]

        # get fraction injected in primary site
        if primary_inj_site_fieldname == 'all': # then sites could be different for each brain 
            print("all injection sites")
            frac_injections = []
            primary_injection_sites = rows.values_list('primary_inj_site',flat=True)
            for ii,row in enumerate(rows):
                primary_injection_site = primary_injection_sites[ii]
                primary_inj_site_fieldname = primary_inj_site_dict[primary_injection_site]
                frac_injection = getattr(row,f'frac_inj_{primary_inj_site_fieldname}')
                # frac_injection =
                frac_injections.append(frac_injection)
        else:
            frac_injections = rows.values_list(f'frac_inj_{primary_inj_site_fieldname}')
            primary_injection_sites = [primary_inj_site for _ in frac_injections]

        serializer = ViralTracingSerializer({
            'brain_names':brain_names,
            'primary_inj_sites':primary_injection_sites,
            'frac_injections':frac_injections,
            'brain_urls':brain_urls})

        return Response(serializer.data)


##### Below are classes/methods for displaying data on the brainsharer public frontend

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 500

class SmallResultsSetPagination(PageNumberPagination):
    page_size = 50


class NeuroglancerAvailableData(viewsets.ModelViewSet):
    """
    API endpoint that allows the available neuroglancer data on the server
    to be viewed.
    """
    queryset = NeuroglancerView.objects.all()
    serializer_class = NeuroglancerViewSerializer
    pagination_class = SmallResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given animal,
        by filtering against a `animal` query parameter in the URL.
        """
        queryset = NeuroglancerView.objects.all()
        animal = self.request.query_params.get('animal')
        lab = self.request.query_params.get('lab')
        layer_type = self.request.query_params.get('layer_type')
        if animal is not None:
            queryset = queryset.filter(group_name__icontains=animal)
        if lab is not None and int(lab) > 0:
            queryset = queryset.filter(lab=lab)
        if layer_type is not None and layer_type != '':
            queryset = queryset.filter(layer_type=layer_type)

        return queryset


class NeuroglancerViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows the neuroglancer states to be viewed or edited.
    Note, the update, and insert methods are over ridden in the serializer.
    It was more convienent to do them there than here.
    """
    serializer_class = NeuroglancerStateSerializer
    pagination_class = SmallResultsSetPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given animal,
        by filtering against a `animal` query parameter in the URL.
        """
        queryset = NeuroglancerState.objects.filter(public=True).order_by('comments')
        comments = self.request.query_params.get('comments')
        lab = self.request.query_params.get('lab')
        if comments is not None:
            queryset = queryset.filter(comments__icontains=comments)
        if lab is not None and int(lab) > 0:
            queryset = queryset.filter(owner__lab=lab)

        return queryset


class NeuroglancerGroupAvailableData(views.APIView):
    """
    API endpoint that allows the available neuroglancer data on the server
    to be viewed.
    """
    queryset = NeuroglancerView.objects.all()
    serializer_class = NeuroglancerGroupViewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        Just getting distinct group_name and layer_type
        for the frontend create-view page
        """
        data = NeuroglancerView.objects.order_by('group_name', 'layer_type').values('group_name', 'layer_type').distinct()
        serializer = NeuroglancerGroupViewSerializer(data, many=True)
        return Response(serializer.data)



@api_view(['POST'])
def create_state(request):
    if request.method == "POST":
        data = request.data
        layers = []
        data = [i for i in data if not (i['id'] == 0)]
        titles = []
        state = prepare_top_attributes(data[0])
        for d in data:
            id = int(d['id'])
            if id > 0:
                layer = create_layer(d)
                layers.append(layer)
                title = f"{d['group_name']} {d['layer_name']}" 
                titles.append(title)
        state['layers'] = layers
        bottom = prepare_bottom_attributes()
        state.update(bottom)
        state_id = create_neuroglancer_model(state, titles)
        return JsonResponse(state_id, safe=False)
