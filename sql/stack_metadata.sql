select 
a.prep_id as stack, 
h.orientation as cutting_plane,
h.counterstain as stain,
h.section_thickness as section_thickness
from animal a
inner join histology h on a.prep_id = h.prep_id;
