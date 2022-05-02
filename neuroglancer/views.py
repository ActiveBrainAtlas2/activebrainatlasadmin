from neuroglancer.atlas import align_atlas, get_scales
from django.shortcuts import render
from rest_framework import viewsets, views
from rest_framework import permissions
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from django.utils.html import escape
from django.apps import apps
import numpy as np
from neuroglancer.models import Animal
from neuroglancer.serializers import AnimalInputSerializer, \
    AnnotationSerializer, AnnotationsSerializer, \
    IdSerializer, PolygonSerializer, RotationSerializer, UrlSerializer
from neuroglancer.models import UrlModel, BrainRegion, StructureCom,CellType
from neuroglancer.annotation_controller import create_polygons, random_string    
from abakit.lib.annotation_layer import AnnotationLayer
from abakit.atlas.VolumeMaker import VolumeMaker
from abakit.atlas.NgSegmentMaker import NgConverter
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
from neuroglancer.AnnotationManager import AnnotationManager
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

    def get(self, request, obj, prep_id, label, format=None):
        data = []
        annotation_model = apps.get_model(app_label='neuroglancer', model_name=obj)
        try:
            animal = Animal.objects.get(pk=prep_id)
        except Animal.DoesNotExist:
            print('No animal, returning empty list')
            return data
        try:
            rows = annotation_model.objects.filter(annotation_session__animal=animal)\
                        .filter(label=label)
        except:
            print('bad query')
        print('len rows', len(rows))
        
        scale_xy, z_scale = get_scales(prep_id)
        # Working with polygons/lines is much different        
        # first do the lines/polygons
        polygon_points = []
        for row in rows:
            row.x = row.x / scale_xy
            row.y = row.y / scale_xy
            row.z = row.z / z_scale +0.5
            if 'polygon' in row.annotation_session.brain_region.abbreviation.lower():
                polygon_points.append(row)
            else:
                point_annotation = {}
                point_annotation['id'] = random_string()
                point_annotation['point'] = [int(round(row.x)), int(round(row.y)), row.z]
                point_annotation['type'] = 'point'
                if 'COM' in label or 'Rough Alignment' in label:
                    point_annotation['description'] = row.annotation_session.brain_region.abbreviation
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
    url is of the the form:
    https://activebrainatlas.ucsd.edu/activebrainatlas/annotations
    """

    def get(self, request, format=None):
        """
        This will get the layer_data
        """
        data = []
        coms = StructureCom.objects.order_by('annotation_session')\
            .values('annotation_session__animal__prep_id', 'label', 'source').distinct()
        for com in coms:
            data.append({
                "prep_id":com['annotation_session__animal__prep_id'],
                "label":com['label'],
                "source":com['source'],
                })
        serializer = AnnotationsSerializer(data, many=True)
        return Response(serializer.data)


class Rotation(views.APIView):
    """This will be run when a user clicks the align link/button in Neuroglancer
    It will return the json rotation and translation matrix
    Fetch center of mass for the prep_id.
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/rotation/DK39
    Where DK39 is the prep_id
    """

    def get(self, request, prep_id, format=None):

        data = {}
        # if request.user.is_authenticated and animal:
        R, t = align_atlas(prep_id)
        data['rotation'] = R.tolist()
        data['translation'] = t.tolist()

        return JsonResponse(data)


class Rotations(views.APIView):
    '''
    url is of the the form https://activebrainatlas.ucsd.edu/activebrainatlas/rotations
    '''

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
                    StructureCom.objects.all().filter(prep=prep_id)\
                        .filter(brain_region=brain_region).exists() 
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

    def make_volumes(self,volume,animal = 'DK55'):
        vmaker = VolumeMaker(animal,check_path = False)
        structure,contours = volume.get_volume_name_and_contours()
        vmaker.set_aligned_contours({structure:contours})
        vmaker.compute_COMs_origins_and_volumes()
        res = vmaker.get_resolution()
        segment_properties = vmaker.get_segment_properties(structures_to_include=[structure])
        folder_name = f'{animal}_{structure}'
        output_dir = os.path.join(vmaker.path.segmentation_layer,folder_name)
        maker = NgConverter(volume = vmaker.volumes[structure].astype(np.uint8),scales = [res*1000,res*1000,20000],offset=list(vmaker.origins[structure]))
        maker.create_neuroglancer_files(output_dir,segment_properties)
        return folder_name

class SaveAnnotation(views.APIView):
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
    def get(self, request, format=None):
        data = {}
        cell_types = CellType.objects.filter(active=True).all()
        data['cell_type'] = [i.cell_type for i in cell_types]
        return JsonResponse(data)