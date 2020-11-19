

-- CREATE ALGORITHM=UNDEFINED DEFINER='dklab'@'%' SQL SECURITY DEFINER VIEW view_sections AS 
select 
a.prep_id AS prep_id,
sc.section_number AS section_number,
(case when (sc.id = NULL) then 'Placeholder' else 'OK' end) AS include_tif,
(case when (sc.channel = 0) then sc.file_name end) AS ch1_file_path,
(case when (sc.channel = 1) then sc.file_name end) AS ch2_file_path,
(case when (sc.channel = 2) then sc.file_name end) AS ch3_file_path,
(case when (sc.channel = 3) then sc.file_name end) AS ch4_file_path 
from row_sequence rs 
left join slide_czi_to_tif sc on rs.counter = sc.section_number
join slide s on sc.slide_id = s.id
join scan_run sr on s.scan_run_id = sr.id
join animal a on sr.prep_id = a.prep_id;
