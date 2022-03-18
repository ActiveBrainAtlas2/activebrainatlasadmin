import numpy as np
from statistics import mode
from scipy.interpolate import splprep, splev
from collections import OrderedDict
import string
import random

def create_polygons(polygons:list) -> list:
    '''
    Takes all the polygon x,y,z data and turns them into
    Neuroglancer polygons
    :param polygons: dictionary of polygon: x,y,z values
    Interpolates out to a max of 50 splines. I just picked
    50 as a nice round number
    '''
    data = []
    for parent_id, polygon in polygons.items(): 
        n = len(polygon)
        hexcolor = "#FFF000"
        tmp_dict = OrderedDict() # create initial parent/source starting point
        tmp_dict["id"] = parent_id
        tmp_dict["source"] = list(polygon[0])
        tmp_dict["type"] = "polygon"
        child_ids = [random_string() for _ in range(n)]
        tmp_dict["childAnnotationIds"] = child_ids
        tmp_dict["props"] = [hexcolor]
        data.append(tmp_dict)
        for i in range(n-1):
            tmp_dict = OrderedDict()
            pointA = polygon[i]
            pointB = polygon[i + 1]
            tmp_dict["id"] = child_ids[i]
            tmp_dict["pointA"] = pointA
            tmp_dict["pointB"] = pointB
            tmp_dict["type"] = "line"
            tmp_dict["parentAnnotationId"] = parent_id
            tmp_dict["props"] = [hexcolor]
            data.append(tmp_dict)
        tmp_dict = OrderedDict()
        pointA = polygon[-1]
        pointB = polygon[0]
        tmp_dict["id"] = child_ids[-1]
        tmp_dict["pointA"] = pointA
        tmp_dict["pointB"] = pointB
        tmp_dict["type"] = "line"
        tmp_dict["parentAnnotationId"] = parent_id
        tmp_dict["props"] = [hexcolor]
        data.append(tmp_dict)
    return data


def interpolate2d(points:list, new_len:int) -> list:
    '''
    Interpolates a list of tuples to the specified length. The points param
    must be a list of tuples in 2d
    :param points: list of floats
    :param new_len: integer you want to interpolate to. This will be the new
    length of the array
    There can't be any consecutive identical points or an error will be thrown
    unique_rows = np.unique(original_array, axis=0)
    '''
    points = np.array(points)
    lastcolumn = np.round(points[:,-1])
    z = mode(lastcolumn)
    points2d = np.delete(points, -1, axis=1)
    pu = points2d.astype(int)
    indexes = np.unique(pu, axis=0, return_index=True)[1]
    points = np.array([points2d[index] for index in sorted(indexes)])
    addme = points2d[0].reshape(1, 2)
    points2d = np.concatenate((points2d, addme), axis=0)

    tck, u = splprep(points2d.T, u=None, s=3, per=1)
    u_new = np.linspace(u.min(), u.max(), new_len)
    x_array, y_array = splev(u_new, tck, der=0)
    arr_2d = np.concatenate([x_array[:, None], y_array[:, None]], axis=1)
    arr_3d = np.c_[ arr_2d, np.zeros(new_len)+z ] 
    return list(map(tuple, arr_3d))


 
 
# Given three collinear points p, q, r, 
# the function checks if point q lies
# on line segment 'pr'
def onSegment(p:tuple, q:tuple, r:tuple) -> bool:
     
    if ((q[0] <= max(p[0], r[0])) &
        (q[0] >= min(p[0], r[0])) &
        (q[1] <= max(p[1], r[1])) &
        (q[1] >= min(p[1], r[1]))):
        return True
         
    return False
 
# To find orientation of ordered triplet (p, q, r).
# The function returns following values
# 0 --> p, q and r are collinear
# 1 --> Clockwise
# 2 --> Counterclockwise
def orientation(p:tuple, q:tuple, r:tuple) -> int:
     
    val = (((q[1] - p[1]) *
            (r[0] - q[0])) -
           ((q[0] - p[0]) *
            (r[1] - q[1])))
            
    if val == 0:
        return 0
    if val > 0:
        return 1 # Collinear
    else:
        return 2 # Clock or counterclock
 
def doIntersect(p1, q1, p2, q2):
     
    # Find the four orientations needed for 
    # general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
 
    # General case
    if (o1 != o2) and (o3 != o4):
        return True
     
    # Special Cases
    # p1, q1 and p2 are collinear and
    # p2 lies on segment p1q1
    if (o1 == 0) and (onSegment(p1, p2, q1)):
        return True
 
    # p1, q1 and p2 are collinear and
    # q2 lies on segment p1q1
    if (o2 == 0) and (onSegment(p1, q2, q1)):
        return True
 
    # p2, q2 and p1 are collinear and
    # p1 lies on segment p2q2
    if (o3 == 0) and (onSegment(p2, p1, q2)):
        return True
 
    # p2, q2 and q1 are collinear and
    # q1 lies on segment p2q2
    if (o4 == 0) and (onSegment(p2, q1, q2)):
        return True
 
    return False
 
# Returns true if the point p lies 
# inside the polygon[] with n vertices
def is_inside_polygon(points:list) -> bool:
     
    n = len(points)
    coords = np.array(points)
    coords = np.unique(coords, axis=0)
    center = list(coords.mean(axis=0))
     
    # There must be at least 3 vertices
    # in polygon
    if n < 3:
        return False
         
    # Define Infinite (Using INT_MAX 
    # caused overflow problems)
    INT_MAX = 10000    # Create a point for line segment
    # from p to infinite
    extreme = (INT_MAX, center[1])
    count = i = 0
     
    while True:
        next = (i + 1) % n
         
        # Check if the line segment from 'p' to 
        # 'extreme' intersects with the line 
        # segment from 'polygon[i]' to 'polygon[next]'
        if (doIntersect(points[i],
                        points[next],
                        center, extreme)):
                             
            # If the point 'p' is collinear with line 
            # segment 'i-next', then check if it lies 
            # on segment. If it lies, return true, otherwise false
            if orientation(points[i], center,
                           points[next]) == 0:
                return onSegment(points[i], center,
                                 points[next])
                                  
            count += 1
             
        i = next
         
        if (i == 0):
            break
         
    # Return true if count is odd, false otherwise
    return (count % 2 == 1)


def random_string() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=40))


def sort_from_center(polygon:list) -> list:
    '''
    Get the center of the unique points in a polygon and then use math.atan2 to get
    the angle from the x-axis to the x,y point. Use that to sort.
    This only works with convex shaped polygons.
    :param polygon:
    '''
    coords = np.array(polygon)
    coords = np.unique(coords, axis=0)
    center = coords.mean(axis=0)
    centered = coords - center
    angles = -np.arctan2(centered[:,1], centered[:,0])
    sorted_coords = coords[np.argsort(angles)]
    return list(map(tuple, sorted_coords))


def zCrossProduct(a, b, c):
    return (a[0] - b[0]) * (b[1] - c[1]) - (a[1] - b[1]) * (b[0] - c[0])


def is_convex(vertices:list) -> list:
    if len(vertices) < 4:
        return True
    signs = [zCrossProduct(a, b, c) > 0 for a, b, c in zip(vertices[2:], vertices[1:], vertices)]
    return all(signs) or not any(signs)
