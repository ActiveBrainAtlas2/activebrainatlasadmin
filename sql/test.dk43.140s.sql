select id,source_file,section_number,active,channel 
from raw_section where prep_id = 'DK43'  
and source_file in (
'DK43_slide063_2020_01_31__8115_S4_C1.tif',
'DK43_slide063_2020_01_31__8115_S4_C2.tif',
'DK43_slide063_2020_01_31__8115_S4_C3.tif',
'DK43_slide063_2020_01_31__8115_S3_C1.tif',
'DK43_slide063_2020_01_31__8115_S3_C2.tif',
'DK43_slide063_2020_01_31__8115_S3_C3.tif'
)
order by section_number,channel;
