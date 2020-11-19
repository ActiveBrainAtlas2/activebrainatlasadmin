select 
 concat("ls -1 ",source_file) as operation
-- concat("convert ",source_file," -compress lzw ../preps/CH2/full/", lpad(section_number,3,0),".tif") as operation
from raw_section 
where prep_id = 'DK39' and active = 1 and channel = 2 
order by section_number
