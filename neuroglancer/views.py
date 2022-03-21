from neuroglancer.atlas import align_atlas, get_scales
from django.shortcuts import render
from rest_framework import viewsets, views
from rest_framework import permissions
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from django.utils.html import escape
from django.http import Http404
from collections import OrderedDict

import numpy as np
from neuroglancer.models import Animal
from neuroglancer.serializers import AnimalInputSerializer, \
    AnnotationSerializer, AnnotationsSerializer, \
    IdSerializer, PolygonSerializer, RotationSerializer, UrlSerializer
from neuroglancer.models import InputType, UrlModel, AnnotationPoints, \
    BrainRegion
from neuroglancer.annotation_controller import create_polygons, random_string    
    
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)


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
        R, t = align_atlas(animal)
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
        polygons = OrderedDict()
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
        for row in rows:
            x = row.x / scale_xy
            y = row.y / scale_xy
            z = int(round(row.z / z_scale))+0.5
            if 'polygon' in row.brain_region.abbreviation.lower():
                segment_id = row.segment_id
                polygons.setdefault(segment_id, []).append((x,y,z))
            
            else:
                tmp_dict = {}
                tmp_dict['id'] = random_string()
                tmp_dict['point'] = [int(round(x)), int(round(y)), z]
                tmp_dict['type'] = 'point'
                if 'COM' in label or 'Rough Alignment' in label:
                    tmp_dict['description'] = row.brain_region.abbreviation
                else:
                    tmp_dict['description'] = ""
                data.append(tmp_dict)
        if len(polygons) > 0:
            data = create_polygons(polygons)
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

    def get(self, request, prep_id, input_type, owner_id, format=None):

        input_type_id = get_input_type_id(input_type)
        data = {}
        # if request.user.is_authenticated and animal:
        R, t = align_atlas(prep_id, input_type_id=input_type_id,
                           owner_id=owner_id)
        data['rotation'] = R.tolist()
        data['translation'] = t.tolist()

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
