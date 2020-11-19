update raw_section set section_number = section_number + 8 where prep_id = 'DK39' and section_number > 200;


insert into raw_section (prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)
select 
prep_id, 201 as section_number, tif_id, slide_physical_id, scene_number, channel, source_file, 
CONCAT('DK39_PH_',LPAD(201,4,0),'_slide_',LPAD(slide_physical_id,0,3),'S',scene_number,'_C',channel,'.tif') as destination_file,
file_status, active, NOW()
from raw_section where section_number = 200 and prep_id = 'DK39';

insert into raw_section (prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)
select 
prep_id, 202 as section_number, tif_id, slide_physical_id, scene_number, channel, source_file, 
CONCAT('DK39_PH_',LPAD(202,4,0),'_slide_',LPAD(slide_physical_id,0,3),'S',scene_number,'_C',channel,'.tif') as destination_file,
file_status, active, NOW()
from raw_section where section_number = 200 and prep_id = 'DK39';

insert into raw_section (prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)
select 
prep_id, 203 as section_number, tif_id, slide_physical_id, scene_number, channel, source_file, 
CONCAT('DK39_PH_',LPAD(203,4,0),'_slide_',LPAD(slide_physical_id,0,3),'S',scene_number,'_C',channel,'.tif') as destination_file,
file_status, active, NOW()
from raw_section where section_number = 200 and prep_id = 'DK39';

insert into raw_section (prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)
select 
prep_id, 204 as section_number, tif_id, slide_physical_id, scene_number, channel, source_file, 
CONCAT('DK39_PH_',LPAD(204,4,0),'_slide_',LPAD(slide_physical_id,0,3),'S',scene_number,'_C',channel,'.tif') as destination_file,
file_status, active, NOW()
from raw_section where section_number = 200 and prep_id = 'DK39';

-- now 4 more inserts


insert into raw_section (prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)
select 
prep_id, 205 as section_number, tif_id, slide_physical_id, scene_number, channel, source_file, 
CONCAT('DK39_PH_',LPAD(205,4,0),'_slide_',LPAD(slide_physical_id,0,3),'S',scene_number,'_C',channel,'.tif') as destination_file,
file_status, active, NOW()
from raw_section where section_number = 209 and prep_id = 'DK39';

insert into raw_section (prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)
select 
prep_id, 206 as section_number, tif_id, slide_physical_id, scene_number, channel, source_file, 
CONCAT('DK39_PH_',LPAD(206,4,0),'_slide_',LPAD(slide_physical_id,0,3),'S',scene_number,'_C',channel,'.tif') as destination_file,
file_status, active, NOW()
from raw_section where section_number = 209 and prep_id = 'DK39';

insert into raw_section (prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)
select 
prep_id, 207 as section_number, tif_id, slide_physical_id, scene_number, channel, source_file, 
CONCAT('DK39_PH_',LPAD(207,4,0),'_slide_',LPAD(slide_physical_id,0,3),'S',scene_number,'_C',channel,'.tif') as destination_file,
file_status, active, NOW()
from raw_section where section_number = 209 and prep_id = 'DK39';


insert into raw_section (prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)
select 
prep_id, 208 as section_number, tif_id, slide_physical_id, scene_number, channel, source_file, 
CONCAT('DK39_PH_',LPAD(208,4,0),'_slide_',LPAD(slide_physical_id,0,3),'S',scene_number,'_C',channel,'.tif') as destination_file,
file_status, active, NOW()
from raw_section where section_number = 209 and prep_id = 'DK39';


-- | section_number | destination_file                | channel |
-- +----------------+---------------------------------+---------+
-- |            200 | DK39_ID_0595_slide050_S4_C1.tif |       1 |
-- |            200 | DK39_ID_0596_slide050_S4_C2.tif |       2 |
-- |            200 | DK39_ID_0597_slide050_S4_C3.tif |       3 |
-- |            209 | DK39_ID_0601_slide053_S1_C1.tif |       1 |
-- |            209 | DK39_ID_0602_slide053_S1_C2.tif |       2 |
-- |            209 | DK39_ID_0603_slide053_S1_C3.tif |       3 |
