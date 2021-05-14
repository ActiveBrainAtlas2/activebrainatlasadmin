import json
from neuroglancer.atlas import align_atlas, brain_to_atlas_transform
from django.shortcuts import render
from rest_framework import viewsets, views
from rest_framework import permissions
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from django.utils.html import escape
from django.http import Http404
import string
import random


from neuroglancer.serializers import RotationSerializer, UrlSerializer, CenterOfMassSerializer, \
    AnimalInputSerializer, IdSerializer
from neuroglancer.models import CenterOfMass, UrlModel
from brain.models import ScanRun

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
    # lookup_field = "id"


class CenterOfMassViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows centers of mass to be viewed or edited.
    """
    queryset = CenterOfMass.objects.all()
    serializer_class = CenterOfMassSerializer
    permission_classes = [permissions.AllowAny]
    # lookup_field = "id"


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

# from url initial page


def public_list(request):
    """
    Shows a listing of urls made available to the public
    :param request:
    :return:
    """
    urls = UrlModel.objects.filter(public=True).order_by('comments')
    return render(request, 'public.html', {'urls': urls})

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


class PointList(views.APIView):
    """
    Fetch UrlModel and return parsed annotation layer.
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/annotation/164/COM
    Where 164 is the primary key of the model and 'COM' is the layer name
    """

    def get(self, request, pk, layer_name, format=None):
        points = []
        try:
            urlModel = UrlModel.objects.filter(
                pk=pk).filter(url__has_key='layers')[0]
            json_txt = urlModel.url
            layers = json_txt['layers']
            for layer in layers:
                if 'annotations' in layer:
                    annotation = layer['annotations']
                    if len(annotation) > 0 and layer_name in layer['name']:
                        points = annotation
        except UrlModel.DoesNotExist:
            raise Http404

        return JsonResponse(points, safe=False)


class ComPointList(views.APIView):
    """
    Fetch UrlModel and return parsed annotation layer.
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/annotation/DK52/2
    Where DK52 is the primary key of the model and 'COM' is the layer name
    """

    def get(self, request, prep_id, person_id, format=None):
        
        def random_string():
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))

        points = []
        
        try:
            coms = CenterOfMass.objects.filter(prep_id=prep_id)\
                .filter(transformation__active=True)\
                .filter(person_id=person_id).all()
        except CenterOfMass.DoesNotExist:
            raise Http404

        R, t = align_atlas(prep_id, input_type='manual', person_id=person_id)

        for com in coms:
            point_dict = {}
            coords = (com.x, com.y, com.section)
            x,y,z = brain_to_atlas_transform(coords, R, t) 
            point_dict['point'] = [x, y, z]
            point_dict['type'] = "point"
            point_dict['id'] = random_string()
            point_dict['description'] = com.structure.abbreviation
            points.append(point_dict)

        return JsonResponse(points, safe=False)


class AnnotationList(views.APIView):
    """
    Fetch UrlModel and return a list of dictionaries:
    {'id': 213, 'description': 'DK39 COM Test', 'layer_name': 'COM'}
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/annotations
    """

    def get_aligned_centers(self, layer_keys):
        coms = CenterOfMass.objects.order_by('prep_id', 'person_id', 'input_type')\
            .filter(active=True)\
            .filter(transformation__active=True)\
            .values('prep_id', 'input_type', 'person_id', 'person__username').distinct()

        for com in coms:
            layer_keys.append(
                {"id": com['prep_id'],
                 "description": f"{com['prep_id']} COM {com['person__username']}",
                 "layer_name": com['person_id']})

        return layer_keys

    def get(self, request, format=None):
        """
        new version with JSON column
        """
        layer_keys = []
        urlModels = UrlModel.objects.filter(vetted=True)\
            .filter(url__has_key='layers')
        for urlModel in urlModels:
            json_txt = urlModel.url
            layers = json_txt['layers']
            for layer in layers:
                if 'annotations' in layer and 'name' in layer:
                    annotation = layer['annotations']
                    layer_name = layer['name']
                    if len(annotation) > 0:
                        layer_keys.append(
                            {"id": urlModel.id,
                            "description": urlModel.comments[0:15],
                             "layer_name": layer_name})
        all_layers = self.get_aligned_centers(layer_keys)

        return JsonResponse(all_layers, safe=False)


class RotationList(views.APIView):
    """
    Fetch distinct prep_id, input_type, person_id and username:
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/rotations
    """

    def get(self, request, format=None):
        queryset = CenterOfMass.objects.order_by('prep_id', 'person_id', 'input_type')\
            .filter(active=True).filter(input_type__in=['detected', 'manual'])\
            .values('prep_id', 'input_type', 'person_id', 'person__username').distinct()
        serializer = RotationSerializer(queryset, many=True)
        return Response(serializer.data)


class Rotation(views.APIView):
    """This will be run when a user clicks the align link/button in Neuroglancer
    It will return the json rotation and translation matrix
    Fetch center of mass for the prep_id, input_type and person_id.
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/rotation/DK39/manual/2
    Where DK39 is the prep_id, manual is the input_type and 2 is the person_id
    """

    def get(self, request, prep_id, input_type, person_id, format=None):
        serializer = RotationSerializer(
            data={'prep_id': prep_id, 'input_type': input_type, 'person_id':person_id})
        serializer.is_valid(self)

        data = {}
        # if request.user.is_authenticated and animal:
        R, t = align_atlas(prep_id, input_type=input_type, person_id=person_id)
        data['rotation'] = R.tolist()
        data['translation'] = t.tolist()

        return JsonResponse(data)


class CenterOfMassList(views.APIView):
    """
    List all COM. No creation at this time.
    """

    def get(self, request, format=None):
        coms = CenterOfMass.objects.filter(active=True).order_by('prep_id')
        serializer = CenterOfMassSerializer(coms, many=True)
        return Response(serializer.data)
