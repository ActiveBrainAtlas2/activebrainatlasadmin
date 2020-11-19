SELECT
-- s.scene_qc_1 as qc1,
-- s.scene_qc_2 as qc2,
-- s.scene_qc_3 as qc3,
-- s.scene_qc_4 as qc4,
-- s.insert_before_one as ibf1, 
-- s.insert_between_one_two as ib_1_2,
sc.scene_number as SN,
sc.scene_index as SI,
sc.channel_index AS CI,
sc.file_name as "file name tif                         ",
sc.active

FROM animal a
INNER JOIN scan_run sr ON a.prep_id = sr.prep_id
INNER JOIN slide s ON sr.id = s.scan_run_id
INNER JOIN slide_czi_to_tif sc ON s.id = sc.slide_id
WHERE a.prep_id = 'DK39'
-- and sc.channel_index = 0
-- and sc.id > 19015
ORDER BY sc.file_name,sc.scene_number, sc.section_number; 
