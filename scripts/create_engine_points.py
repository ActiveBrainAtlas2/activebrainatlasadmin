import os, sys
import argparse

HOME = os.path.expanduser("~")
PATH = os.path.join(HOME, 'programming/activebrainatlas')
sys.path.append(PATH)
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "activebrainatlas.settings")
import django
from django.db import connection
django.setup()

from neuroglancer.models import LayerData
STRUCTURE_ID = 52


def create_layer(animal, layer, id, start, debug):

    with connection.cursor() as cursor:
        sql = """select el.frame, el.points 
                from engine_labeledshape el  
                inner join engine_label elab on el.label_id = elab.id
                where elab.task_id = %s 
                order by el.frame"""
        cursor.execute(sql, [id])
        rows = cursor.fetchall()
    count = 1
    for row in rows:
        section = row[0] + start
        points = row[1]
        s = points.split(',')
        points = map(','.join, zip(s[::2], s[1::2]))
        for point in points:
            x,y = point.split(',')
            x = float(x)
            y = float(y)
            x *= 32
            y *= 32
            if debug:
                print(count, section, x, y)
                count += 1
            else:
                LayerData.objects.create(prep_id=animal, structure_id = STRUCTURE_ID, person_id=1,
                                                layer=layer, input_type_id = 1,
                                                x=x,y=y,section=section)    
    



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Work on Animal')
    parser.add_argument('--id', help='Enter ID', required=True)
    parser.add_argument('--animal', help='Enter animal', required=True)    
    parser.add_argument('--layer', help='Enter layer name', required=True)    
    parser.add_argument('--start', help='Enter start', required=True)
    parser.add_argument('--debug', help='Enter debug True|False', required=False, default='false')

    args = parser.parse_args()
    animal = args.animal
    layer = args.layer
    id = int(args.id)
    start = int(args.start)
    debug = bool({'true': True, 'false': False}[str(args.debug).lower()])
    create_layer(animal, layer, id, start, debug)




                
        


