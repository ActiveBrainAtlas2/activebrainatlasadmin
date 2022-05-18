import json
from neuroglancer.atlas import align_stack_to_atlas, get_scales
from django.shortcuts import render
from rest_framework import viewsets, views
from rest_framework import permissions
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from django.utils.html import escape
from django.http import Http404
import numpy as np
from neuroglancer.models import Animal
from neuroglancer.serializers import AnimalInputSerializer, \
    AnnotationSerializer, AnnotationsSerializer, \
    IdSerializer, PolygonSerializer, RotationSerializer, UrlSerializer
from neuroglancer.models import InputType, UrlModel, AnnotationPoints, \
    BrainRegion
from neuroglancer.annotation_controller import create_polygons, random_string    
from abakit.lib.annotation_layer import AnnotationLayer
import logging
from abakit.atlas.VolumeMaker import VolumeMaker
from abakit.atlas.NgSegmentMaker import NgConverter
import numpy as np
from abakit.lib.annotation_layer import AnnotationLayer
import os
logging.basicConfig()
logger = logging.getLogger(__name__)
from neuroglancer.tasks import move_annotations,bulk_annotations
from brain.models import ScanRun
from abakit.lib.FileLocationManager import FileLocationManager
class UrlViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows the neuroglancer urls to be viewed or edited.
    """
    queryset = UrlModel.objects.all()
    serializer_class = UrlSerializer
    permission_classes = [permissions.AllowAny]


class AlignAtlasView(views.APIView):
    """This will be run when a user clicks the align link/button in Neuroglancer
    It will return the json rotation and translation matrix"""

    def get(self, request, *args, **kwargs):
        # Validate the incoming input (provided through query parameters)
        serializer = AnimalInputSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        animal = serializer.validated_data['animal']
        data = {}
        # if request.user.is_authenticated and animal:
        R, t = align_stack_to_atlas(animal)
        rl = R.tolist()
        tl = t.tolist()
        data['rotation'] = rl
        data['translation'] = tl

        return JsonResponse(data)


class UrlDataView(views.APIView):
    """This will be run when a a ID is sent to:
    https://site.com/activebrainatlas/urldata?id=999
    Where 999 is the primary key of the url model"""

    def get(self, request, *args, **kwargs):
        # Validate the incoming input (provided through query parameters)
        serializer = IdSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        id = serializer.validated_data['id']
        urlModel = UrlModel.objects.get(pk=id)
        return HttpResponse(f"#!{escape(urlModel.url)}")

class Annotation(views.APIView):
    """
    Fetch LayerData model and return parsed annotation layer.
    url is of the the form
    https://activebrainatlas.ucsd.edu/activebrainatlas/annotation/DKXX/premotor/2
    Where:
         DKXX is the animal,
         premotor is the label,
         2 is the input type ID
    """

    def get(self, request, prep_id, label, input_type_id, format=None):
        data = []
        try:
            animal = Animal.objects.get(pk=prep_id)
        except Animal.DoesNotExist:
            return data

        rows = AnnotationPoints.objects.filter(animal=animal)\
                    .filter(label=label)\
                    .filter(input_type_id=input_type_id)\
                    .filter(active=True)\
                    .order_by('ordering')
        
        scale_xy, z_scale = get_scales(prep_id)
        # Working with polygons/lines is much different        
        # first do the lines/polygons
        polygon_points = []
        for row in rows:
            row.x = row.x / scale_xy
            row.y = row.y / scale_xy
            row.z = row.z / z_scale +0.5
            if 'polygon' in row.brain_region.abbreviation.lower():
                polygon_points.append(row)
            else:
                point_annotation = {}
                point_annotation['id'] = random_string()
                point_annotation['point'] = [int(round(row.x)), int(round(row.y)), row.z]
                point_annotation['type'] = 'point'
                if 'COM' in label or 'Rough Alignment' in label:
                    point_annotation['description'] = row.brain_region.abbreviation
                else:
                    point_annotation['description'] = ""
                data.append(point_annotation)
        if len(polygon_points) > 0:
            data = create_polygons(polygon_points)
            serializer = PolygonSerializer(data, many=True)
        else:
            serializer = AnnotationSerializer(data, many=True)

        return Response(serializer.data)
        # return JsonResponse(data, safe=False)

class Annotations(views.APIView):
    """
    Fetch UrlModel and return a set of two dictionaries. 
    One is from the layer_data
    table and the other is the COMs that have been set as transformations.
    {'id': 213, 'description': 'DK39 COM Test', 'label': 'COM'}
    url is of the the form:
    https://activebrainatlas.ucsd.edu/activebrainatlas/annotations
    """

    def get(self, request, format=None):
        """
        This will get the layer_data
        """
        data = []
        state_layers = AnnotationPoints.objects.order_by('animal__prep_id', 'label', 'input_type_id')\
            .filter(active=True).filter(input_type_id__in=[1, 3, 5 , 6 , 7, 4, 11])\
            .filter(label__isnull=False)\
            .values('animal__prep_id', 'label', 'input_type__input_type', 'input_type_id')\
            .distinct()
        for state_layer in state_layers:
            data.append({
                "prep_id":state_layer['animal__prep_id'],
                "label":state_layer['label'],
                "input_type":state_layer['input_type__input_type'],
                "input_type_id":state_layer['input_type_id'],
                })
        serializer = AnnotationsSerializer(data, many=True)
        return Response(serializer.data)


class Rotation(views.APIView):
    """This will be run when a user clicks the align link/button in Neuroglancer
    It will return the json rotation and translation matrix
    Fetch center of mass for the prep_id, input_type and owner_id.
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/rotation/DK39/manual/2
    Where DK39 is the prep_id, manual is the input_type and 2 is the owner_id
    """

    def get(self, request, prep_id, input_type, owner_id,reverse = 0, format=None,reference_scales = 'None'):

        input_type_id = get_input_type_id(input_type)
        data = {}
        # if request.user.is_authenticated and animal:
        R, t = align_stack_to_atlas(prep_id, input_type_id=input_type_id,
                           owner_id=owner_id,reverse=reverse==1,reference_scales = eval(reference_scales))
        data['rotation'] = R.tolist()
        data['translation'] = t.tolist()
        result = ScanRun.objects.filter(prep_id=prep_id).first()
        if result:
            data['resolution'] = [result.resolution,result.resolution,result.zresolution]
        else:
            data['resolution'] = None
        return JsonResponse(data)

class Rotations(views.APIView):
    """
    Fetch distinct prep_id, input_type, owner_id and username:
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/rotations
    Note: animal is an animal object, while the prep_id is the name of the animal
    """

    def get(self, request, format=None):
        data = []
        com_manual = AnnotationPoints.objects.order_by('animal__prep_id', 'owner_id', 'input_type_id')\
            .filter(label='COM').filter(owner_id=2)\
            .filter(active=True).filter(input_type__input_type__in=['manual'])\
            .values('animal__prep_id', 'input_type__input_type', 'owner_id', 'owner__username').distinct()
        com_detected = AnnotationPoints.objects.order_by('animal__prep_id', 'owner_id', 'input_type_id')\
            .filter(label='COM').filter(owner_id=23)\
            .filter(active=True).filter(input_type__input_type__in=['detected'])\
            .values('animal__prep_id', 'input_type__input_type', 'owner_id', 'owner__username').distinct()
        for com in com_manual:
            data.append({
                "prep_id":com['animal__prep_id'],
                "input_type":com['input_type__input_type'],
                "owner_id":com['owner_id'],
                "username":com['owner__username'],
                })
        for com in com_detected:
            data.append({
                "prep_id":com['animal__prep_id'],
                "input_type":com['input_type__input_type'],
                "owner_id":com['owner_id'],
                "username":com['owner__username'],
                })
        serializer = RotationSerializer(data, many=True)
        return Response(serializer.data)


def get_input_type_id(input_type):
    input_type_id = 0
    try:
        input_types = InputType.objects.filter(input_type=input_type).filter(active=True).all()
    except InputType.DoesNotExist:
        raise Http404

    if len(input_types) > 0:
        input_type = input_types[0]
        input_type_id = input_type.id

    return input_type_id

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

    def get(self, request, format=None):

        list_of_landmarks = BrainRegion.objects.all().filter(active=True).all()
        list_of_landmarks = [i.abbreviation for i in list_of_landmarks]
        data = {}
        data['land_marks'] = list_of_landmarks
        return JsonResponse(data)


class AnnotationStatus(views.APIView):

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
                    AnnotationPoints.objects.all().filter(active=True).filter(prep=prep_id)\
                        .filter(layer='COM').filter(brain_region=brain_region).exists() 
                counts = has_annotation.sum(axis=0)
        return render(request, 'annotation_status.html', {'has_annotation': has_annotation, 'animals': list_of_animals, \
            'brain_regions': list_of_landmarks_name, 'counts': counts})
        
        # return HttpResponse(has_annotation)

class ContoursToVolume(views.APIView):
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
    
    def downsample_contours(self,contours,downsample_factor):
        values = [i/downsample_factor for i in contours.values()]
        return dict(zip(contours.keys(),values))
    
    def get_scale(self,animal,downsample_factor):
        scan_run = ScanRun.objects.filter(prep_id = animal).first()
        res = scan_run.resolution
        return [downsample_factor*res*1000,downsample_factor*res*1000,scan_run.zresolution*1000]

    def make_volumes(self,volume,animal = 'DK55',downsample_factor = 100):
        vmaker = VolumeMaker()
        structure,contours = volume.get_volume_name_and_contours()
        downsampled_contours = self.downsample_contours(contours,downsample_factor)
        vmaker.set_aligned_contours({structure:downsampled_contours})
        vmaker.compute_origins_and_volumes_for_all_segments()
        volume = (vmaker.volumes[structure]).astype(np.uint8)
        offset = list(vmaker.origins[structure])
        folder_name = f'{animal}_{structure}'
        path = FileLocationManager(animal)
        output_dir = os.path.join(path.segmentation_layer,folder_name)
        scale = self.get_scale(animal,downsample_factor)
        maker = NgConverter(volume = volume,scales = scale,offset=offset)
        maker.create_neuroglancer_files(output_dir,segment_properties=[(1,structure)])
        return folder_name

class SaveAnnotation(views.APIView):
    def get(self, request, url_id,annotation_layer_name):
        urlModel = UrlModel.objects.get(pk=url_id)
        state_json = urlModel.url
        layers = state_json['layers']
        found = False
        for layeri in layers:
            if layeri['type'] == 'annotation':
                if layeri['name'] == annotation_layer_name:
                    prep_id = Animal.objects.get(pk=urlModel.animal).prep_id
                    owner = urlModel.owner.id
                    move_annotations(prep_id, owner, annotation_layer_name)
                    bulk_annotations(prep_id, layeri, owner, annotation_layer_name)
                    found = True
        if found:
            return Response('success')
        else:
            return Response(f'layer not found {(annotation_layer_name)}')