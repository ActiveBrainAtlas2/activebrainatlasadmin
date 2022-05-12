from neuroglancer.atlas import align_atlas, get_scales
from django.shortcuts import render
from rest_framework import viewsets, views
from rest_framework import permissions
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from django.utils.html import escape
from django.apps import apps
import numpy as np
from neuroglancer.models import  AnnotationSession, MarkedCell, PolygonSequence
from neuroglancer.serializers import AnnotationSerializer, ComListSerializer,MarkedCellSerializer,PolygonListSerializer, \
    IdSerializer, PolygonSerializer, RotationSerializer, UrlSerializer
from neuroglancer.models import UrlModel, BrainRegion, StructureCom,CellType
from neuroglancer.annotation_controller import create_polygons, random_string    
from neuroglancer.AnnotationBase import AnnotationBase
from abakit.lib.annotation_layer import AnnotationLayer
from abakit.atlas.VolumeMaker import VolumeMaker
from abakit.atlas.NgSegmentMaker import NgConverter
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
from neuroglancer.AnnotationManager import AnnotationManager
import os 

class UrlViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows the neuroglancer urls to be viewed or edited.
    """
    queryset = UrlModel.objects.all()
    serializer_class = UrlSerializer
    permission_classes = [permissions.AllowAny]


class UrlDataView(views.APIView):
    """This is the API component that allows neuroglancer to fetch the json state for a perticular entry in the neuroglancer_url table

    Args:
        The row id in neuroglancer_url is passed to the function in the request variable.  This is part of django formats

    Returns:
        HttpResponse: a http page with the json state as the content
    """

    def get(self, request, *args, **kwargs):
        # Validate the incoming input (provided through query parameters)
        serializer = IdSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        id = serializer.validated_data['id']
        urlModel = UrlModel.objects.get(pk=id)
        return HttpResponse(f"#!{escape(urlModel.url)}")

def create_point_annotation(coordinates,description):
    """create annotation points in the neuroglancer json format

    Args:
        coordinates (list): list of coordinates: x,y,z for this annotation point
        description (str): the description field of this annotation point.  This would be displayed in neuroglancer 

    Returns:
        _type_: _description_
    """    
    point_annotation = {}
    point_annotation['id'] = random_string()
    point_annotation['point'] = coordinates
    point_annotation['type'] = 'point'
    point_annotation['description'] = description
    return point_annotation

def apply_scales_to_annotation_rows(rows,prep_id):
    """To fetch the scan resolution of an animal from the database and apply it to a list of annotation rows

    Args:
        rows (list): list of query result from either the StructureCom, MarkedCell or PolygonSequence table
        prep_id (string): animal id
    """    
    scale_xy, z_scale = get_scales(prep_id)
    for row in rows:
        row.x = row.x / scale_xy
        row.y = row.y / scale_xy
        row.z = row.z / z_scale +0.5
    data = create_polygons(rows)

class GetVolume(AnnotationBase,views.APIView):
    """
    view that returns the volume annotation for a session in neuroglancer json format
    """

    def get(self, request, obj, session_id, format=None):
        try:
            session = AnnotationSession.objects.get(pk=session_id)
            rows = PolygonSequence.objects.filter(annotation_session__pk=session_id)
        except:
            print('bad query')
        print('len rows', len(rows))
        apply_scales_to_annotation_rows(rows,session.animal.prep_id)
        data = create_polygons(rows)
        serializer = PolygonSerializer(data, many=True)
        return Response(serializer.data)

class GetCOM(AnnotationBase,views.APIView):
    '''view that returns the COM for a perticular annotator in neuroglancer json format'''
    def get(self, request, obj, prep_id, annotator_id,source, format=None):
        self.set_animal_from_id(prep_id)
        self.set_annotator_from_id(annotator_id)
        try:
            rows = StructureCom.objects.filter(annotation_session__animal=self.animal)\
                        .filter(source=source).filter(annotator=self.annotator)
        except:
            print('bad query')
        print('len rows', len(rows))
        apply_scales_to_annotation_rows(rows,self.animal.prep_id)
        data = []
        for row in rows:
            coordinates = [int(round(row.x)), int(round(row.y)), row.z]
            description = row.annotation_session.brain_region.abbreviation
            point_annotation = create_point_annotation(coordinates,description)
            data.append(point_annotation)
        serializer = AnnotationSerializer(data, many=True)
        return Response(serializer.data)

class GetMarkedCell(AnnotationBase,views.APIView):
    '''view that returns the marked cells for a specific annotation session in neuroglancer json format'''
    def get(self, request, obj, session_id, format=None):
        try:
            session = AnnotationSession.objects.get(pk=session_id)
            rows = MarkedCell.objects.filter(annotation_session__pk=session_id)
        except:
            print('bad query')
        print('len rows', len(rows))
        apply_scales_to_annotation_rows(rows,session.animal.prep_id)
        data = []
        for row in rows:
            coordinates = [int(round(row.x)), int(round(row.y)), row.z]
            point_annotation = create_point_annotation(coordinates,'')
            data.append(point_annotation)
        serializer = AnnotationSerializer(data, many=True)
        return Response(serializer.data)

class GetComList(views.APIView):
    """
    view that returns a list of available COMs
    """

    def get(self, request, format=None):
        """
        This will get the layer_data
        """
        data = []
        coms = StructureCom.objects.order_by('annotation_session')\
            .values('annotation_session__animal__prep_id', 'annotation_session__annotator__username', 'source').distinct()
        for com in coms:
            data.append({
                "prep_id":com['annotation_session__animal__prep_id'],
                "annotator":com['annotation_session__annotator__username'],
                "source":com['source'],
                })
        serializer = ComListSerializer(data, many=True)
        return Response(serializer.data)


class GetPolygonList(views.APIView):
    """
    view that returns a list of available brain region volumes
    """

    def get(self, request, format=None):
        """
        This will get the layer_data
        """
        data = []
        active_sessions = AnnotationSession.objects.filter(active=True).objects.filter(annotation_type='POLYGON_SEQUENCE')\
            .values('animal__prep_id', 'annotator__username','brain_region__abbreviation', 'source','id').all()
        for sessioni in active_sessions:
            data.append({
                'id' : sessioni['id'],
                "prep_id":sessioni['animal__prep_id'],
                "annotator":sessioni['annotator__username'],
                "brain_region":sessioni['brain_region__abbreviation'],
                "source":sessioni['source'],
                })
        serializer = PolygonListSerializer(data, many=True)
        return Response(serializer.data)

class GetMarkedCellList(views.APIView):
    """
    view that returns a list of available marked cell annotations
    """

    def get(self, request, format=None):
        """
        This will get the layer_data
        """
        data = []
        active_sessions = AnnotationSession.objects.filter(active=True).objects.filter(annotation_type='MARKED_CELL')\
            .values('animal__prep_id', 'annotator__username','brain_region__abbreviation', 'source','id').all()
        for sessioni in active_sessions:
            data.append({
                'id' : sessioni['id'],
                "prep_id":sessioni['annotation_session__animal__prep_id'],
                "annotator":sessioni['annotator__username'],
                "source":sessioni['source'],
                })
        serializer = MarkedCellSerializer(data, many=True)
        return Response(serializer.data)

class Rotation(views.APIView):
    """view that returns the transformation from the atlas to the image of one perticular brain.
    prep_id: the animal id, not the primary key in the animal table
    """

    def get(self, request, prep_id, format=None):

        data = {}
        # if request.user.is_authenticated and animal:
        R, t = align_atlas(prep_id)
        data['rotation'] = R.tolist()
        data['translation'] = t.tolist()

        return JsonResponse(data)

class Rotations(views.APIView):
    '''view that returns the available set of rotations'''

    def get(self, request, format=None):
        data = []
        coms = StructureCom.objects.order_by('annotation_session')\
            .values('annotation_session__animal__prep_id', 'label', 'source').distinct()
        for com in coms:
            data.append({
                "prep_id":com['annotation_session__animal__prep_id'],
                "label":com['label'],
                "source":com['source'],
                })
        serializer = RotationSerializer(data, many=True)
        return Response(serializer.data)
        
def load_layers(request):
    layers = []
    url_id = request.GET.get('id')
    urlModel = UrlModel.objects.get(pk=url_id).all()
    if urlModel.layers is not None:
        layers = urlModel.layers
    return render(request, 'layer_dropdown_list_options.html', {'layers': layers})

def public_list(request):
    """
    Shows a listing of urls made available to the public
    :param request:
    :return:
    """
    urls = UrlModel.objects.filter(public=True).order_by('comments')
    return render(request, 'public.html', {'urls': urls})

class LandmarkList(views.APIView):
    '''View that returns a list of active brain regions in the structures table'''
    def get(self, request, format=None):

        list_of_landmarks = BrainRegion.objects.all().filter(active=True).all()
        list_of_landmarks = [i.abbreviation for i in list_of_landmarks]
        data = {}
        data['land_marks'] = list_of_landmarks
        return JsonResponse(data)


class AnnotationStatus(views.APIView):
    '''View that returns the current status of COM annotations.  This is to be updated or depricated'''
    def get(self, request, format=None):
        list_of_landmarks = BrainRegion.objects.all().filter(active=True).all()
        list_of_landmarks_id = [i.id for i in list_of_landmarks]
        list_of_landmarks_name = [i.abbreviation for i in list_of_landmarks]
        list_of_animals = ['DK39', 'DK41', 'DK43', 'DK46', 'DK52', 'DK54', 'DK55', 'DK61', \
            'DK62', 'DK63']
        n_landmarks = len(list_of_landmarks_id)
        n_animals = len(list_of_animals)
        has_annotation = np.zeros([n_landmarks, n_animals])
        for animali in range(n_animals):
            for landmarki in range(n_landmarks):
                prep_id = list_of_animals[animali]
                brain_region = list_of_landmarks_id[landmarki]
                has_annotation[landmarki, animali] = \
                    StructureCom.objects.all().filter(prep=prep_id)\
                        .filter(brain_region=brain_region).exists() 
                counts = has_annotation.sum(axis=0)
        return render(request, 'annotation_status.html', {'has_annotation': has_annotation, 'animals': list_of_animals, \
            'brain_regions': list_of_landmarks_name, 'counts': counts})
        
class ContoursToVolume(views.APIView):
    '''View that convert a volume in a specific neuroglancer url to a 3d mask.  The view finds the volume according to
    the volume id, and creates the 3d volume according the contours contained within'''
    def get(self, request, url_id,volume_id):
        urlModel = UrlModel.objects.get(pk=url_id)
        state_json = urlModel.url
        layers = state_json['layers']
        for layeri in layers:
            if layeri['type'] == 'annotation':
                layer = AnnotationLayer(layeri)
                volume = layer.get_annotation_with_id(volume_id)
                if volume is not None:
                    break
        folder_name = self.make_volumes(volume,urlModel.animal)
        segmentation_save_folder = f"precomputed://https://activebrainatlas.ucsd.edu/data/structures/{folder_name}" 
        return JsonResponse({'url':segmentation_save_folder,'name':folder_name})

    def make_volumes(self,volume,animal = 'DK55'):
        vmaker = VolumeMaker(animal,check_path = False)
        structure,contours = volume.get_volume_name_and_contours()
        vmaker.set_aligned_contours({structure:contours})
        vmaker.compute_COMs_origins_and_volumes()
        res = vmaker.get_resolution()
        print('=============================================')
        print(res)
        segment_properties = vmaker.get_segment_properties(structures_to_include=[structure])
        folder_name = f'{animal}_{structure}'
        output_dir = os.path.join(vmaker.path.segmentation_layer,folder_name)
        maker = NgConverter(volume = vmaker.volumes[structure].astype(np.uint8),scales = [res*1000,res*1000,20000],offset=list(vmaker.origins[structure]))
        maker.create_neuroglancer_files(output_dir,segment_properties)
        return folder_name

class SaveAnnotation(views.APIView):
    '''View that saves all the annotation in one annotation layer of a specific row in the neuroglancer url table'''
    def get(self, request, url_id,annotation_layer_name):
        urlModel = UrlModel.objects.get(pk=url_id)
        state_json = urlModel.url
        layers = state_json['layers']
        found = False
        manager = AnnotationManager(urlModel)
        for layeri in layers:
            if layeri['type'] == 'annotation':
                if layeri['name'] == annotation_layer_name:
                    manager.set_current_layer(layeri)
                    manager.update_data_in_current_layer()
                    found = True
        if found:
            return Response('success')
        else:
            return Response(f'layer not found {(annotation_layer_name)}')

class GetCellTypes(views.APIView):
    '''View that returns a list of cell types'''
    def get(self, request, format=None):
        data = {}
        cell_types = CellType.objects.filter(active=True).all()
        data['cell_type'] = [i.cell_type for i in cell_types]
        return JsonResponse(data)