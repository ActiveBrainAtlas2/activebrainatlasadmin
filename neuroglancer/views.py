import json
from django.shortcuts import render
from rest_framework import viewsets, generics, views
from rest_framework import permissions
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from django.utils.html import escape
from django.http import Http404
import numpy as np
import string
import random


from neuroglancer.serializers import RotationSerializer, UrlSerializer, CenterOfMassSerializer, \
    AnimalInputSerializer, IdSerializer, PointSerializer
from neuroglancer.models import UrlModel, CenterOfMass, ROW_LENGTH, COL_LENGTH, Z_LENGTH, \
    ATLAS_RAW_SCALE, ATLAS_X_BOX_SCALE, ATLAS_Y_BOX_SCALE, ATLAS_Z_BOX_SCALE
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
        #if request.user.is_authenticated and animal:
        R, t = align_atlas(animal)
        rl = R.tolist()
        tl = t.tolist()
        data['rotation'] = rl
        data['translation'] = tl

        return JsonResponse(data)

def align_point_sets(src, dst, with_scaling=True):
    """
    Analytically computes a transformation that minimizes the squared error between source and destination.
    ------------------------------------------------------
    src is the dictionary of the brain we want to align
    dst is the dictionary of the atlas structures
    Defaults to scaling true, which means the transformation is rigid and a uniform scale.
    returns the linear transformation r, and the translation vector t
    """
    assert src.shape == dst.shape
    assert len(src.shape) == 2
    m, n = src.shape  # dimension, number of points

    src_mean = np.mean(src, axis=1).reshape(-1, 1)
    dst_mean = np.mean(dst, axis=1).reshape(-1, 1)

    src_demean = src - src_mean
    dst_demean = dst - dst_mean

    u, s, vh = np.linalg.svd(dst_demean @ src_demean.T / n)

    # deal with reflection
    e = np.ones(m)
    if np.linalg.det(u) * np.linalg.det(vh) < 0:
        print('reflection detected')
        e[-1] = -1

    r = u @ np.diag(e) @ vh

    if with_scaling:
        src_var = (src_demean ** 2).sum(axis=0).mean()
        c = sum(s * e) / src_var
        r *= c

    t = dst_mean - r @ src_mean
    return r, t

def align_atlas(animal, input_type=None, person_id=None):
    """
    This prepares the data for the align_point_sets method.
    Make sure we have at least 3 points
    :param animal: the animal we are aligning to
    :return: a 3x3 matrix and a 1x3 matrix
    """
    atlas_box_size=(ROW_LENGTH, COL_LENGTH, Z_LENGTH)
    atlas_box_scales=(ATLAS_X_BOX_SCALE, ATLAS_Y_BOX_SCALE, ATLAS_Z_BOX_SCALE)
    atlas_centers = get_atlas_centers(atlas_box_size, atlas_box_scales, ATLAS_RAW_SCALE)
    reference_centers = get_centers_dict(animal, input_type=input_type, person_id=person_id)
    try:
        scanRun = ScanRun.objects.get(prep__prep_id=animal)
    except ScanRun.DoesNotExist:
        scanRun = None

    if len(reference_centers) > 2 and scanRun is not None:
        resolution = scanRun.resolution
        reference_scales = (resolution, resolution, ATLAS_Z_BOX_SCALE)
        structures = sorted(reference_centers.keys())
        # align animal to atlas
        common_keys = atlas_centers.keys() & reference_centers.keys()
        dst_point_set = np.array([atlas_centers[s] for s in structures if s in common_keys]).T
        dst_point_set = np.diag(atlas_box_scales) @ dst_point_set
        src_point_set = np.array([reference_centers[s] for s in structures if s in common_keys]).T
        src_point_set = np.diag(reference_scales) @ src_point_set

        R, t = align_point_sets(src_point_set, dst_point_set)
        #t = t / np.array([reference_scales]).T
        t = t / np.array([atlas_box_scales]).T

    else:
        R = np.eye(3)
        t = np.zeros(3)
        t = t.reshape(3,1)
    return R, t

def brain_to_atlas_transform(brain_coord, r, t):
    """
    Takes an x,y,z brain coordinates, and a rotation matrix and transform vector.
    Returns the point in atlas coordinates. 
    """
    atlas_coord = []
    return atlas_coord

def atlas_to_brain_transform(atlas_coord, r, t):
    pass


def get_atlas_centers(
        atlas_box_size=(1000, 1000, 300),
        atlas_box_scales=(10, 10, 20),
        atlas_raw_scale=10):
    atlas_box_scales = np.array(atlas_box_scales)
    atlas_box_size = np.array(atlas_box_size)
    atlas_box_center = atlas_box_size / 2
    atlas_centers = get_centers_dict('atlas')

    for structure, origin in atlas_centers.items():
        # transform into the atlas box coordinates that neuroglancer assumes
        center = atlas_box_center + np.array(origin) * atlas_raw_scale / atlas_box_scales
        atlas_centers[structure] = center

    return atlas_centers

def get_centers_dict(prep_id, input_type=None, person_id=None):
    rows = CenterOfMass.objects.filter(prep__prep_id=prep_id).filter(active=True).order_by('structure', 'updated')
    if input_type is not None:
        rows = rows.filter(input_type=input_type)
    if person_id is not None:
        rows = rows.filter(person_id=person_id)
    

    row_dict = {}
    for row in rows:
        structure = row.structure.abbreviation
        row_dict[structure] = [row.x, row.y, row.section]

    return row_dict


# from url initial page
def public_list(request):
    """
    Shows a listing of urls made available to the public
    :param request:
    :return:
    """
    urls = UrlModel.objects.filter(public=True).order_by('comments')
    return render(request, 'public.html',{'urls': urls})

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
            urlModel = UrlModel.objects.get(pk=pk)
            json_txt = json.loads(urlModel.url)
            layers = {}
            if 'layers' in json_txt:
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
            return ''.join(random.choices(string.ascii_lowercase + string.digits, k = 40))

        points = []
        try:
            coms = CenterOfMass.objects.filter(prep_id=prep_id)\
                .filter(input_type='aligned')\
                .filter(person_id=person_id).all()
            for com in coms:
                point_dict = {}
                point_dict['point'] = [com.x, com.y, com.section]
                point_dict['type'] = "point"
                point_dict['id'] = random_string()
                point_dict['description'] = com.structure.abbreviation
                points.append(point_dict)
        except CenterOfMass.DoesNotExist:
            raise Http404

        return JsonResponse(points, safe=False)


class AnnotationList(views.APIView):
    """
    Fetch UrlModel and return a list of dictionaries:
    {'id': 213, 'description': 'DK39 COM Test', 'layer_name': 'COM'}
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/annotations
    """
    def get_aligned_centers(self, layer_keys):
        DESC = 'aligned'
        coms = CenterOfMass.objects.order_by('prep_id', 'person_id', 'input_type')\
            .filter(active=True)\
            .filter(input_type=DESC)\
            .values('prep_id', 'input_type', 'person_id', 'person__username').distinct()

        for com in coms:
            layer_keys.append(
                {"id":com['prep_id'], 
                "description": f"{com['prep_id']} COM {com['person__username']}", 
                "layer_name":com['person_id']})

        return layer_keys

    def get(self, request, format=None):
        layer_keys = []
        urlModels = UrlModel.objects.filter(vetted=True)
        for urlModel in urlModels:
            json_txt = json.loads(urlModel.url)
            if 'layers' in json_txt:
                layers = json_txt['layers']
            for layer in layers:
                if 'annotations' in layer and 'name' in layer:
                    annotation = layer['annotations']
                    layer_name = layer['name']
                    if len(annotation) > 0:
                        layer_keys.append(
                            {"id":urlModel.id, 
                            "description":urlModel.comments[0:15], 
                            "layer_name":layer_name})
        all_layers = self.get_aligned_centers(layer_keys)

        return JsonResponse(all_layers, safe=False)


class RotationList(views.APIView):
    """
    Fetch distinct prep_id, input_type, person_id and username:
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/rotations
    """

    def get(self, request, format=None):
        queryset = CenterOfMass.objects.order_by('prep_id', 'person_id', 'input_type')\
            .filter(active=True)\
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
            data={'prep_id':prep_id, 'input_type':input_type, 'person_id':person_id})
        serializer.is_valid(self)

        data = {}
        #if request.user.is_authenticated and animal:
        R, t = align_atlas(prep_id, input_type=input_type, person_id=person_id)
        data['rotation'] = R.tolist()
        data['translation'] = t.tolist()

        return JsonResponse(data)




class CenterOfMassList(views.APIView):
    """
    List all animals. No creation at this time.
    """
    def get(self, request, format=None):
        coms = CenterOfMass.objects.filter(active=True).order_by('prep_id')
        serializer = CenterOfMassSerializer(coms, many=True)
        return Response(serializer.data)

