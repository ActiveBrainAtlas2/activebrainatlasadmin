"""This is the module that the user will use to connect to the database.
This can be defined in either a web page or in a REST API call. This module
is the 'V' in the MVC framework for the Neuroglancer app
portion of the portal.
"""

import decimal
from django.db.models import Count
from rest_framework import viewsets, views, permissions, status
from django.http import JsonResponse
from rest_framework.response import Response
from neuroglancer.annotation_controller import create_polygons
from neuroglancer.annotation_base import AnnotationBase
from neuroglancer.annotation_layer import random_string, create_point_annotation
from neuroglancer.annotation_manager import DEBUG
from neuroglancer.atlas import align_atlas, get_scales
from neuroglancer.models import UNMARKED, AnnotationSession, MarkedCell, PolygonSequence, \
    UrlModel, BrainRegion, StructureCom, CellType
from neuroglancer.serializers import AnnotationSerializer, ComListSerializer, \
    MarkedCellListSerializer, PolygonListSerializer, \
    PolygonSerializer, RotationSerializer, UrlSerializer
from neuroglancer.tasks import background_archive_and_insert_annotations, \
    nobackground_archive_and_insert_annotations
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
from subprocess import check_output
import os
from time import sleep

class UrlViewSet(viewsets.ModelViewSet):
    """API endpoint that allows the neuroglancer urls to be viewed or edited.
    """
    
    queryset = UrlModel.objects.all()
    serializer_class = UrlSerializer
    permission_classes = [permissions.AllowAny]

def apply_scales_to_annotation_rows(rows, prep_id):
    """To fetch the scan resolution of an animal from the database and apply it to a 
    list of annotation rows

    :param rows: list of query result from either the StructureCom, MarkedCell, 
        or PolygonSequence table.
    :param prep_id: string animal id
    """

    scale_xy, z_scale = get_scales(prep_id)
    for row in rows:
        row.x = row.x / scale_xy
        row.y = row.y / scale_xy
        row.z = row.z / z_scale + decimal.Decimal(0.5)


class GetVolume(AnnotationBase, views.APIView):
    """A view that returns the volume annotation for a session in neuroglancer json format
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
    """A view that returns the COM for a perticular annotator in neuroglancer json format
    """

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
    """A view that returns the marked cells for a specific annotation session in neuroglancer json format.
    """

    def get(self, request, session_id, format=None):
        try:
            session = AnnotationSession.objects.get(pk=session_id)
        except:
            return Response({"Error": "Record does not exist"}, status=status.HTTP_404_NOT_FOUND)
        rows = MarkedCell.objects.filter(annotation_session__pk=session_id)
        apply_scales_to_annotation_rows(rows, session.animal.prep_id)
        data = []
        for row in rows:
            coordinates = [int(round(row.x)), int(round(row.y)), row.z]
            description = row.source
            if row.source == 'HUMAN_POSITIVE':
                description = 'positive'
            elif row.source == 'HUMAN_NEGATIVE':
                description = 'negative'
            elif row.source == 'MACHINE_SURE':
                description = 'machine_sure'
            elif row.source == 'MACHINE_UNSURE':
                description = 'machine_unsure'
            elif row.source == UNMARKED:
                description = 'unmarked'
            else:
                return Response({"Error": "Source is not correct on annotation session"}, status=status.HTTP_404_NOT_FOUND)
                
             
            point_annotation = create_point_annotation(coordinates, description, type='cell')
            point_annotation['category'] = row.cell_type.cell_type
            data.append(point_annotation)
        serializer = AnnotationSerializer(data, many=True)
        return Response(serializer.data)


class GetComList(views.APIView):
    """A view that returns a list of available COMs.
    """

    def get(self, request, format=None):
        """
        This will get the layers of COMs for the dropdown menu
        """
        data = []
        coms = StructureCom.objects.order_by('annotation_session__animal__prep_id', 
            'annotation_session__annotator__username')\
            .values('annotation_session__animal__prep_id', 'annotation_session__annotator__username', 
            'annotation_session__annotator__id', 'source')\
            .annotate(Count("id"))
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
    """A view that returns a list of available brain region volumes.
    """

    def get(self, request, format=None):
        """
        This will get the layer_data
        """
        data = []
        rows = AnnotationSession.objects.filter(
            active=True).filter(annotation_type='POLYGON_SEQUENCE').all()
        for row in rows:
            data.append({
                'session_id': row.id,
                "prep_id": row.animal.prep_id,
                "annotator": row.annotator.username,
                "brain_region": row.brain_region.abbreviation,
                "source": 'NA'
            })
        serializer = PolygonListSerializer(data, many=True)
        return Response(serializer.data)


class GetMarkedCellList(views.APIView):
    """A view that returns a list of available marked cell annotations.
    """

    def get(self, request, format=None):
        """
        This will get the layer_data for the marked cell requested
        """
        data = []
        rows = MarkedCell.objects.filter(annotation_session__active=True)\
            .order_by('annotation_session__animal', 
            'annotation_session__annotator__username')\
            .values('annotation_session__id',
            'annotation_session__animal', 
            'annotation_session__annotator__username',
            'source',
            'cell_type__cell_type',
            'cell_type__id',
            'annotation_session__brain_region__abbreviation',
            'annotation_session__brain_region__id',
            )\
            .distinct()

        for row in rows:
            data.append({
                'session_id': row['annotation_session__id'],
                'prep_id': row['annotation_session__animal'],
                'annotator': row['annotation_session__annotator__username'],
                'source': row['source'],
                'cell_type': row['cell_type__cell_type'],
                'cell_type_id': row['cell_type__id'],
                'structure': row['annotation_session__brain_region__abbreviation'],
                'structure_id': row['annotation_session__brain_region__id'],
            })
        serializer = MarkedCellListSerializer(data, many=True)
        return Response(serializer.data)



class Rotation(views.APIView):
    """A view that returns the transformation from the atlas to the image stack of one 
    particular brain.
    """

    def get(self, request, prep_id, annotator_id, source, reverse=0, reference_scales='None', format=None):
        data = {}
        R, t = align_atlas(prep_id, annotator_id, source,
                           reverse=reverse, reference_scales=eval(reference_scales))
        data['rotation'] = R.tolist()
        data['translation'] = t.tolist()
        return JsonResponse(data)


class Rotations(views.APIView):
    """A view that returns the available set of rotations.
    """

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


class LandmarkList(views.APIView):
    """A view that returns a list of active brain regions in the structures table.
    """

    def get(self, request, format=None):

        list_of_landmarks = BrainRegion.objects.all().filter(active=True).all()
        list_of_landmarks = [i.abbreviation for i in list_of_landmarks]
        data = {}
        data['land_marks'] = list_of_landmarks
        return JsonResponse(data)


class ContoursToVolume(views.APIView):
    """Method to run slurm to create a 3D volume
    """
    
    def get(self, request, url_id, volume_id):
        command = ["sbatch", os.path.abspath('./slurm_scripts/contour_to_volume'), str(url_id),volume_id]
        print(command)
        out = check_output(command)
        start_id = out.find(b'job')+4
        job_id = int(out[start_id:-1])
        output_file = f'/opt/slurm/output/slurm_{job_id}.out'
        error_file = f'/opt/slurm/output/slurm_{job_id}.err'
        while not os.path.exists(output_file):
            sleep(1)
            print(f'waiting for job {job_id} to finish')
        print('finished')
        text_file = open(output_file, "r")
        data = text_file.read()
        text_file.close()
        url = data.split('\n')[-1]
        folder_name = url.split('/')[-1]
        return JsonResponse({'url': url, 'name': folder_name})

class SaveAnnotation(views.APIView):
    """A view that saves all the annotation in one annotation layer of a specific row in the neuroglancer url table
    There are two methods to save the data, one is in the background and the other is the default way without
    using the background process. We use the background task in production as the method can take a long time
    to complete.
    """
    
    def get(self, request, url_id, annotation_layer_name):
        urlModel = UrlModel.objects.get(pk=url_id)
        state_json = urlModel.url
        layers = state_json['layers']
        found = False
        for layeri in layers:
            if layeri['type'] == 'annotation' and layeri['name'] == annotation_layer_name:

                if DEBUG:
                    nobackground_archive_and_insert_annotations(layeri, url_id)
                else:
                    background_archive_and_insert_annotations(layeri, url_id, verbose_name="Insert annotations", creator=urlModel.owner)
                found = True

        if found:
            return Response('success')
        else:
            return Response(f'layer not found {(annotation_layer_name)}')


class GetCellTypes(views.APIView):
    """View that returns a list of cell types
    """

    def get(self, request, format=None):
        data = {}
        cell_types = CellType.objects.filter(active=True).all()
        data['cell_type'] = [i.cell_type for i in cell_types]
        return JsonResponse(data)
