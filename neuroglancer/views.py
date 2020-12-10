from rest_framework import viewsets
from rest_framework import permissions
from django.http import JsonResponse
from rest_framework import serializers, views
import numpy as np

from neuroglancer.serializers import UrlSerializer, CenterOfMassSerializer
from neuroglancer.models import UrlModel, CenterOfMass
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



class AnimalInputSerializer(serializers.Serializer):
    animal = serializers.CharField()


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

def align_atlas(animal):
    """
    Make sure we have at least 3 points
    :param animal: the animal we are aligning to
    :return: a 3x3 matrix and a 1x3 matrix
    """
    atlas_box_size=(1000, 1000, 300)
    atlas_box_scales=(10, 10, 20)
    atlas_raw_scale=10
    atlas_centers = get_atlas_centers(atlas_box_size, atlas_box_scales, atlas_raw_scale)
    reference_centers = get_centers_dict(animal)
    try:
        scanRun = ScanRun.objects.get(prep__prep_id=animal)
    except ScanRun.DoesNotExist:
        scanRun = None

    if len(reference_centers) > 2 and scanRun is not None:
        resolution = scanRun.resolution
        reference_scales = (resolution, resolution, 20)
        structures = sorted(reference_centers.keys())
        src_point_set = np.array([atlas_centers[s] for s in structures]).T
        src_point_set = np.diag(atlas_box_scales) @ src_point_set
        dst_point_set = np.array([reference_centers[s] for s in structures]).T
        dst_point_set = np.diag(reference_scales) @ dst_point_set
        R, t = align_point_sets(src_point_set, dst_point_set)
        t = t / np.array([reference_scales]).T

    else:
        R = np.eye(3)
        t = np.zeros(3)
        t = t.reshape(3,1)
    return R, t

def get_atlas_centers(
        atlas_box_size=(1000, 1000, 300),
        atlas_box_scales=(10, 10, 20),
        atlas_raw_scale=10):
    atlas_box_scales = np.array(atlas_box_scales)
    atlas_box_size = np.array(atlas_box_size)
    atlas_box_center = atlas_box_size / 2
    atlas_centers = get_centers_dict('Atlas')

    for structure, origin in atlas_centers.items():
        # transform into the atlas box coordinates that neuroglancer assumes
        center = atlas_box_center + np.array(origin) * atlas_raw_scale / atlas_box_scales
        atlas_centers[structure] = center

    return atlas_centers

def get_centers_dict(prep_id):
    rows = CenterOfMass.objects.filter(prep__prep_id=prep_id)
    row_dict = {}
    for row in rows:
        structure = row.structure.abbreviation
        row_dict[structure] = [row.x, row.y, row.section]

    return row_dict


