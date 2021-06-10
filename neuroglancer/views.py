from neuroglancer.atlas import align_atlas
from django.shortcuts import render
from rest_framework import viewsets, views
from rest_framework import permissions
from django.http import JsonResponse, HttpResponse

from rest_framework.response import Response
from django.utils.html import escape
from django.http import Http404
import string
import random


from neuroglancer.serializers import AnnotationSerializer, AnnotationsSerializer, RotationSerializer, UrlSerializer,  \
    AnimalInputSerializer, IdSerializer
from neuroglancer.models import InputType, UrlModel, LayerData

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

class LayerDataViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows centers of mass to be viewed or edited.
    """
    queryset = LayerData.objects.order_by('prep_id').all()
    serializer_class = LayerData
    permission_classes = [permissions.AllowAny]

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
# from urldata request, take the ID of the URL model and return all data in escaped format


class UrlDataView(views.APIView):
    """This will be run when a a ID is sent to https://site.com/activebrainatlas/urldata?id=999
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
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/annotation/DKXX/premotor/2
    Where:
         DKXX is the animal,
         premotor is the layer name,
         2 is the input type ID
    """

    def get(self, request, prep_id, layer_name, input_type_id, format=None):
        points = []
        try:
            layers = LayerData.objects.filter(prep_id=prep_id).filter(layer=layer_name)\
                .filter(input_type_id=input_type_id).filter(active=True).all()
        except LayerData.DoesNotExist:
            raise Http404


        for layer in layers:
            point_dict = {}
            point_dict['point'] = [layer.x, layer.y, layer.section]
            point_dict['type'] = layer.annotation_type
            point_dict['id'] = random_string()
            if 'COM' in layer_name:
                point_dict['description'] = layer.structure.abbreviation
            else:
                point_dict['description'] = ""
            points.append(point_dict)

        serializer = AnnotationSerializer(points, many=True)
        return Response(serializer.data)


class Annotations(views.APIView):
    """
    Fetch UrlModel and return a set of two dictionaries. One is from the layer_data
    table and the other is the COMs that have been set as transformations.
    {'id': 213, 'description': 'DK39 COM Test', 'layer_name': 'COM'}
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/annotations
    """

    def get(self, request, format=None):
        """
        This will get the layer_data
        """
        data = []
        layers = LayerData.objects.order_by('prep_id', 'layer', 'input_type_id')\
            .filter(active=True)\
            .values('prep_id', 'layer','input_type__input_type','input_type_id').distinct()
        for layer in layers:
            data.append({
                "prep_id":layer['prep_id'],
                "layer":layer['layer'],
                "input_type":layer['input_type__input_type'],
                "input_type_id":layer['input_type_id'],                
                })

        serializer = AnnotationsSerializer(data, many=True)
        return Response(serializer.data)


class Rotation(views.APIView):
    """This will be run when a user clicks the align link/button in Neuroglancer
    It will return the json rotation and translation matrix
    Fetch center of mass for the prep_id, input_type and person_id.
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/rotation/DK39/manual/2
    Where DK39 is the prep_id, manual is the input_type and 2 is the person_id
    """

    def get(self, request, prep_id, input_type, person_id, format=None):

        input_type_id = get_input_type_id(input_type)
        data = {}
        # if request.user.is_authenticated and animal:
        R, t = align_atlas(prep_id, input_type_id=input_type_id, person_id=person_id)
        data['rotation'] = R.tolist()
        data['translation'] = t.tolist()

        return JsonResponse(data)


class Rotations(views.APIView):
    """
    Fetch distinct prep_id, input_type, person_id and username:
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/rotations
    """

    def get(self, request, format=None):
        data = []
        coms = LayerData.objects.order_by('prep_id', 'person_id', 'input_type_id')\
            .filter(layer='COM')\
            .filter(active=True).filter(input_type__input_type__in=['detected', 'manual','corrected'])\
            .values('prep_id', 'input_type__input_type', 'person_id', 'person__username').distinct()
        for com in coms:
            data.append({
                "prep_id":com['prep_id'],
                "input_type":com['input_type__input_type'],
                "person_id":com['person_id'],
                "username":com['person__username'],
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

def random_string():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))
        
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

