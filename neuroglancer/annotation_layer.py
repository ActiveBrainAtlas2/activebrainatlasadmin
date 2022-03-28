from tracemalloc import start
import numpy as np
from django.http.response import Http404


class AnnotationLayer:

    def __init__(self, annotation_layer):
        try:
            assert annotation_layer['type'] == 'annotation'
        except:
            raise Http404
        self.annotations = annotation_layer['annotations']
        self.name = annotation_layer['name']
        if 'tool' in annotation_layer:
            self.tool = annotation_layer['tool']
        self.source = annotation_layer['source']
        self.type = 'annotation'
        self.parse_annotations()

    def __str__(self):
            return "str method: annotation_layer is %s, b is %s" % (self.annotation_layer)
    
    def parse_annotations(self):
        annotations = []
        for annotationi in self.annotations:
            if annotationi['type'] == 'polygon':
                annotations.append(self.parse_polygon(annotationi))
            if annotationi['type'] == 'volume':
                annotations.append(self.parse_volume(annotationi))
            elif annotationi['type'] == 'point':
                annotations.append(self.parse_point(annotationi))
            elif annotationi['type'] == 'line':
                annotations.append(self.parse_line(annotationi))
        self.annotations = np.array(annotations)
        self.group_annotations('polygon')
        self.reorder_polygon_points()
        self.group_annotations('volume')
    
    def parse_point(self, point_json):
        point = Point(point_json['point'], point_json['id'])
        if 'description' in point_json:
            point.description = point_json['description']
        return point
    
    def parse_line(self, line_json):
        line = Line(line_json['pointA'], line_json['pointB'], line_json['id'])
        if 'parentAnnotationId' in line_json:
            line.parent_id = line_json['parentAnnotationId']
        if 'description' in line_json:
            line.description = line_json['description']
        return line

    def parse_polygon(self, polygon_json):
        polygon = Polygon(polygon_json['id'], polygon_json['childAnnotationIds'], polygon_json['source'])
        if 'description' in polygon_json:
            polygon.description = polygon_json['description']
        if 'parentAnnotationId' in polygon_json:
            polygon.parent_id = polygon_json['parentAnnotationId']
        return polygon
    
    def parse_volume(self, volume_json):
        volume = Volume(volume_json['id'], volume_json['childAnnotationIds'], volume_json['source'])
        if 'description' in volume_json:
            volume.description = volume_json['description']
        return volume

    def search_annotation_with_id(self, id):
        search_result = [annotationi.id == id for annotationi in self.annotations]
        if sum(search_result) == 0:
            print('annotation not found')
        elif sum(search_result) > 1:
            print('more than one result found')
        return search_result
    
    def group_annotations(self,type):
        for annotationi in self.annotations:
            if annotationi.type == type:
                annotationi.childs=[]
                for childid in annotationi.child_ids:
                    annotationi.childs.append(self.get_annotation_with_id(childid))
                    self.delete_annotation_with_id(childid)
                annotationi.childs = np.array(annotationi.childs)
    
    def reorder_polygon_points(self):
        for annotationi in self.annotations:
            if annotationi.type == 'polygon':
                start_points = np.array([pointi.coord_start for pointi in annotationi.childs])
                end_points = np.array([pointi.coord_end for pointi in annotationi.childs])
                sorter = ContourSorter(start_points=start_points,end_points=end_points,first_point=annotationi.source)
                annotationi.childs = np.array(annotationi.childs)[sorter.sort_index]
                annotationi.child_ids = annotationi.child_ids[sorter.sort_index]

    def get_annotation_with_id(self, id):
        search_result = self.search_annotation_with_id(id)
        return self.annotations[search_result][0]
    
    def delete_annotation_with_id(self, id):
        search_result = self.search_annotation_with_id(id)
        self.annotations = self.annotations[np.logical_not(search_result)]
    
    def to_json(self):
        point_json = {}
        ...


class Point:

    def __init__(self, coord, id):
        self.coord = np.array(coord)
        self.id = id
        self.type = 'point'
    
    def to_json(self):
        point_json = {}
        ...


class Line:

    def __init__(self, coord_start, coord_end, id):
        self.coord_start = np.array(coord_start)
        self.coord_end = np.array(coord_end)
        self.id = id
        self.type = 'line'
        
    def __str__(self):
        return "Line ID is %s, start is %s, end is %s" % (self.id, self.coord_start, self.coord_start)


    def to_json(self):
        ...


class Polygon:

    def __init__(self, id, child_ids, source):
        self.source = source
        self.id = id
        self.child_ids = np.array(child_ids)
        self.type = 'polygon'
        
    def __str__(self):
        return "Polygon ID is %s, source is %s" % (self.id, self.source)
    
    def to_json(self):
        ...

class Volume:

    def __init__(self, id, child_ids, source):
        self.source = source
        self.id = id
        self.child_ids = np.array(child_ids)
        self.type = 'volume'
        
    def __str__(self):
        return "Polygon ID is %s, source is %s" % (self.id, self.source)
    
    def to_json(self):
        ...

class ContourEndReached(Exception):
    pass

class ContourSorter:
    def __init__(self,start_points,end_points,first_point):
        # self.first_point = np.array(first_point)
        self.first_point = np.array(start_points[0])
        self.start_points = np.array(start_points)
        self.end_points = np.array(end_points)
        self.check_input_dimensions()
        self.npoints = len(self.start_points)
        self.sort_index = []
        # first_point_index = self.find_index_of_point_in_array(first_point,self.start_points)
        first_point_index = 0
        self.sort_index.append(first_point_index)
        self.sort_points()

    def check_input_dimensions(self):
        if not self.start_points.shape[1] ==3:
            self.start_points = self.start_points.T
        if not self.end_points.shape[1] ==3:
            self.end_points = self.end_points.T
        assert len(self.start_points) == len(self.end_points)
        assert len(self.start_points[0])==len(self.end_points[0])==len(self.first_point)==3

    def find_index_of_point_in_array(self,point,array,fuzzy = False):
        result = np.where(np.all(array==point,axis = 1))[0]
        if len(result)==1:
            return result[0]
        if len(result)>1:
            idmin = np.argmin(np.abs(result-self.sort_index[-1]))
            return result[idmin]
        if len(result)==0:
            if fuzzy:
                return np.argmin(np.sum(np.abs(array-point),axis=1))
            else:
                raise ContourEndReached
        

    def sort_points(self):
        while len(self.sort_index)<self.npoints:
            current_point_index = self.sort_index[-1]
            try:
                next_point_index = self.find_index_of_next_point(current_point_index)
                self.sort_index.append(next_point_index)
            except ContourEndReached:
                self.sort_index=[current_point_index]
                self.first_point = self.start_points[current_point_index]
                self.revere_sort()
            
        # check_if_contour_points_are_in_order(self.first_point,self.start_points[self.sort_index],self.end_points[self.sort_index])

    def revere_sort(self):
        while len(self.sort_index)<self.npoints:
            current_point_index = self.sort_index[-1]
            try:
                previous_point_index = self.find_index_of_previous_point(current_point_index)
                self.sort_index.append(previous_point_index)
            except ContourEndReached:
                previous_point_index = self.find_index_of_previous_point(current_point_index,fuzzy=True)
                self.sort_index.append(previous_point_index)

    def find_index_of_next_point(self,current_point_index):
        current_point = self.end_points[current_point_index]
        next_start_index = self.find_index_of_point_in_array(current_point,self.start_points)
        return next_start_index
    
    def find_index_of_previous_point(self,current_point_index,fuzzy=False):
        current_point = self.end_points[current_point_index]
        if fuzzy:
            print('fuzzy criteria used')
            next_start_index = self.find_index_of_point_in_array(current_point,self.start_points,fuzzy)
        else:    
            next_start_index = self.find_index_of_point_in_array(current_point,self.start_points)
        return next_start_index
    
def check_if_contour_points_are_in_order(first_point,start_points,end_points):
    assert len(start_points)==len(end_points)
    assert len(start_points[0])==len(end_points[0])==len(first_point)==3
    assert np.all(first_point == start_points[0])
    npoints = len(first_point)
    for i in range(npoints-1):
        assert np.all(start_points[i+1] == end_points[i])
