update raw_section set section_number = section_number + 1 where prep_id = 'DK39' and section_number > 427;


insert into raw_section (prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)
select 
prep_id, 428 as section_number, tif_id, slide_physical_id, scene_number, channel, source_file, 
CONCAT('DK39_PH_',LPAD(428,4,0),'_slide',LPAD(slide_physical_id,3,0),'_S',scene_number,'_C',channel,'.tif') 
as destination_file,
file_status, active, NOW()
from raw_section where section_number = 427 
and prep_id = 'DK39';
