from neuroglancer.models import LayerData
from datetime import datetime
import numpy as np

animal = 'DK39'
structure = 'point'
layer ='detected_soma'
SURE = 6
UNSURE = 7

for i in range (10):
    x,y,z = np.random.rand(3)*10000
    LayerData.objects.create(
        prep=animal, structure=structure, created=datetime.datetime.now(),
        layer = layer, active=True, person='yfreund', input_type_id=SURE,
        x=x, y=y, section=z)

    x,y,z = np.random.rand(3)*10000
    LayerData.objects.create(
        prep=animal, structure=structure, created=datetime.datetime.now(),
        layer = layer, active=True, person='yfreund', input_type_id=UNSURE,
        x=x, y=y, section=z)