from django.db.models import Count
from neuroglancer.AnnotationManager import AnnotationManager
from neuroglancer.atlas import align_atlas, get_scales
from django.shortcuts import render
from rest_framework import viewsets, views
from rest_framework import permissions
from django.http import JsonResponse, HttpResponse
from rest_framework.response import Response
from django.utils.html import escape
import numpy as np
from brain.models import ScanRun
from neuroglancer.models import AnnotationSession, MarkedCell, PolygonSequence
from neuroglancer.serializers import AnnotationSerializer, ComListSerializer, MarkedCellListSerializer, PolygonListSerializer, \
    IdSerializer, PolygonSerializer, RotationSerializer, UrlSerializer
from neuroglancer.models import UrlModel, BrainRegion, StructureCom, CellType
from neuroglancer.annotation_controller import create_polygons
from neuroglancer.AnnotationBase import AnnotationBase
from neuroglancer.annotation_layer import AnnotationLayer, random_string, create_point_annotation
import logging

from neuroglancer.tasks import background_archive_and_insert_annotations
logging.basicConfig()
logger = logging.getLogger(__name__)


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


def apply_scales_to_annotation_rows(rows, prep_id):
    """To fetch the scan resolution of an animal from the database and apply it to a list of annotation rows

    Args:
        rows (list): list of query result from either the StructureCom, MarkedCell or PolygonSequence table
        prep_id (string): animal id
    """
    scale_xy, z_scale = get_scales(prep_id)
    for row in rows:
        row.x = row.x / scale_xy
        row.y = row.y / scale_xy
        row.z = row.z / z_scale + 0.5


class GetVolume(AnnotationBase, views.APIView):
    """
    view that returns the volume annotation for a session in neuroglancer json format
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
    '''view that returns the COM for a perticular annotator in neuroglancer json format'''

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
    '''view that returns the marked cells for a specific annotation session in neuroglancer json format'''

    def get(self, request, session_id, format=None):
        try:
            session = AnnotationSession.objects.get(pk=session_id)
            rows = MarkedCell.objects.filter(annotation_session__pk=session_id)
        except:
            print('bad query')
        apply_scales_to_annotation_rows(rows, session.animal.prep_id)
        data = []
        for row in rows:
            coordinates = [int(round(row.x)), int(round(row.y)), row.z]
            description = row.source
            if description == 'HUMAN_POSITIVE':
                source = 'positive'
            if description == 'HUMAN_NEGATIVE':
                source = 'negative'
            point_annotation = create_point_annotation(
                coordinates, source, type='cell')
            point_annotation['category'] = row.cell_type.cell_type
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
            .values('annotation_session__animal__prep_id', 'annotation_session__annotator__username', 'annotation_session__annotator__id', 'source')\
            .annotate(Count("id")).order_by()
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
    """
    view that returns a list of available brain region volumes
    """

    def get(self, request, format=None):
        """
        This will get the layer_data
        """
        data = []
        active_sessions = AnnotationSession.objects.filter(
            active=True).filter(annotation_type='POLYGON_SEQUENCE').all()
        for sessioni in active_sessions:
            data.append({
                'session_id': sessioni.id,
                "prep_id": sessioni.animal.prep_id,
                "annotator": sessioni.annotator.username,
                "brain_region": sessioni.brain_region.abbreviation,
                "source": sessioni.source,
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
        active_sessions = AnnotationSession.objects.filter(
            active=True).filter(annotation_type='MARKED_CELL').all()
        for sessioni in active_sessions:
            data.append({
                'session_id': sessioni.id,
                "prep_id": sessioni.animal.prep_id,
                "annotator": sessioni.annotator.username,
                "source": sessioni.source,
                "cell_type": sessioni.cell_type.cell_type,
                "cell_type_id": sessioni.cell_type.id,
                "structure": sessioni.brain_region.abbreviation,
                "structure_id": sessioni.brain_region.id,
            })
            if data[-1]['structure'] == 'point':
                data[-1]['structure'] = 'NA'
        serializer = MarkedCellListSerializer(data, many=True)
        return Response(serializer.data)


class Rotation(views.APIView):
    """view that returns the transformation from the atlas to the image of one perticular brain.
    prep_id: the animal id, not the primary key in the animal table
    """

    def get(self, request, prep_id, annotator_id, source, reverse=0, reference_scales='None', format=None):
        data = {}
        R, t = align_atlas(prep_id, annotator_id, source,
                           reverse=reverse, reference_scales=eval(reference_scales))
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
                "prep_id": com['annotation_session__animal__prep_id'],
                "label": com['label'],
                "source": com['source'],
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
        list_of_animals = ['DK39', 'DK41', 'DK43', 'DK46', 'DK52', 'DK54', 'DK55', 'DK61',
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
        return render(request, 'annotation_status.html', {'has_annotation': has_annotation, 'animals': list_of_animals,
                                                          'brain_regions': list_of_landmarks_name, 'counts': counts})


class ContoursToVolume(views.APIView):
    def get(self, request, url_id, volume_id):
        urlModel = UrlModel.objects.get(pk=url_id)
        state_json = urlModel.url
        layers = state_json['layers']
        for layeri in layers:
            if layeri['type'] == 'annotation':
                layer = AnnotationLayer(layeri)
                volume = layer.get_annotation_with_id(volume_id)
                if volume is not None:
                    break
        folder_name = self.make_volumes(volume, urlModel.animal)
        segmentation_save_folder = f"precomputed://https://activebrainatlas.ucsd.edu/data/structures/{folder_name}"
        return JsonResponse({'url': segmentation_save_folder, 'name': folder_name})

    def downsample_contours(self, contours, downsample_factor):
        values = [i/downsample_factor for i in contours.values()]
        return dict(zip(contours.keys(), values))

    def get_scale(self, animal, downsample_factor):
        scan_run = ScanRun.objects.filter(prep_id=animal).first()
        res = scan_run.resolution
        return [downsample_factor*res*1000, downsample_factor*res*1000, scan_run.zresolution*1000]

    def make_volumes(self, volume, animal='DK55', downsample_factor=100):
        pass
        """
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
        """


class SaveAnnotation(views.APIView):
    """View that saves all the annotation in one annotation layer of a specific row in the neuroglancer url table
    There are two methods to save the data, one is in the background and the other is the default way without
    using the background process.
    """

    def get(self, request, url_id, annotation_layer_name):
        urlModel = UrlModel.objects.get(pk=url_id)
        state_json = urlModel.url
        layers = state_json['layers']
        found = False
        manager = AnnotationManager(urlModel)
        for layeri in layers:
            if layeri['type'] == 'annotation' and layeri['name'] == annotation_layer_name:
                    manager.set_current_layer(layeri)
                    if manager.debug:
                        manager.archive_and_insert_annotations()
                    else:
                        background_archive_and_insert_annotations(layeri, url_id)

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
