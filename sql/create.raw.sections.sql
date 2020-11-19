

-- CREATE ALGORITHM=UNDEFINED DEFINER='dklab'@'%' SQL SECURITY DEFINER VIEW view_sections AS 
select 
prep_id,
section_number,
1 as channel,
ch_1_path as source_file,
section_qc as file_status,
active,
created
from section
WHERE a.prep_id = '", PREPID, "'
AND ch_1_path IS NOT NULL

UNION

select 
prep_id,
section_number,
2 as channel,
ch_2_path as source_file,
section_qc as file_status,
active,
created
from section
WHERE a.prep_id = '", PREPID, "'
AND ch_2_path IS NOT NULL

UNION

select 
prep_id,
section_number,
3 as channel,
ch_3_path as source_file,
section_qc as file_status,
active,
created
from section
WHERE a.prep_id = '", PREPID, "'
AND ch_3_path IS NOT NULL

UNION

select 
prep_id,
section_number,
4 as channel,
ch_4_path as source_file,
section_qc as file_status,
active,
created
from section
WHERE a.prep_id = '", PREPID, "'
AND ch_4_path IS NOT NULL;





