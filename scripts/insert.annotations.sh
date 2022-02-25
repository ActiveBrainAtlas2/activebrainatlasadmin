#!/bin/bash

XY_SCALE=".325"
Z_SCALE=20

for i in {1..1000}
do
  #              p = AnnotationPoints.objects.create(animal=self.animal, brain_region=brain_region,
  #                  label=label, owner=self.owner, input_type=self.input_type,
  #                  x=x1, y=y1, z=z1)
    x=$(shuf -i 33200-43300 -n 1)  
    y=$(shuf -i 19000-24000 -n 1)  
    z=$(shuf -i 150-300 -n 1)  
    x1=$(echo "scale=4; $XY_SCALE*$x" | bc)
    y1=$(echo "scale=4; $XY_SCALE*$y" | bc)
    z1=$(echo "scale=4; $Z_SCALE*$z" | bc)
    mysql active_atlas_development<<EOF
    insert into annotations_points (prep_id, FK_structure_id, FK_owner_id, FK_input_id,
    label, x, y, z, active) 
    values ('DK46', 52, 1, 1, 'XXX', $x1, $y1, $z1, 1); 
EOF

done