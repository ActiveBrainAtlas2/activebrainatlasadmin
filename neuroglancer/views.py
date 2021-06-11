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


from neuroglancer.serializers import AnnotationSerializer, AnnotationsSerializer, LineSerializer, RotationSerializer, UrlSerializer,  \
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
            rows = LayerData.objects.filter(prep_id=prep_id).filter(layer=layer_name)\
                .filter(input_type_id=input_type_id).filter(active=True).filter(segment_id=64689).order_by('section','id').all()
        except LayerData.DoesNotExist:
            raise Http404

        if input_type_id != 5:
            for row  in rows:
                point_dict = {}
                point_dict['id'] = random_string()
                point_dict['point'] = [row.x, row.y, row.section]
                point_dict['type'] = row.annotation_type
                            
                if 'COM' in layer_name:
                    point_dict['description'] = row.structure.abbreviation
                else:
                    point_dict['description'] = ""
                points.append(point_dict)
            serializer = AnnotationSerializer(points, many=True)
        else:
            lrows = len(rows) // 2
            for i in range(lrows):
                point_dict = {}
                pointA = rows[i]
                pointB = rows[i+1]
                point_dict['id'] = random_string()
                point_dict['pointA'] = [pointA.x, pointA.y, pointA.section]
                point_dict['pointB'] = [pointB.x, pointB.y, pointB.section]
                point_dict['type'] = 'line'
                point_dict['description'] = ""
                points.append(point_dict)
            serializer = LineSerializer(points, many=True)


        return Response(serializer.data)

"""
json for line:
{
          "id": "6ce1a6e0b25292ed7d95abc19e29beaf61471718",
          "pointA": [
            23453.7265625,
            6428.55322265625,
            236.49998474121094
          ],
          "pointB": [
            25050.107421875,
            11495.3271484375,
            236.49998474121094
          ],
          "type": "line"
        },
json for point
{
          "id": "c6f81a41abdcf7d6b419a3353b982abc03e0a37e",
          "point": [
            47751.0859375,
            21584.93359375,
            276.5000305175781
          ],
          "type": "point"
        }
 """       





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

