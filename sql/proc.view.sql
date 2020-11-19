SELECT
s.slide_physical_id AS SID,
sc.scene_number AS SCN,
MAX(CASE WHEN sc.channel_index = 0 THEN sc.file_name ELSE NULL END) AS 'ch_1_path                                ',
MAX(CASE WHEN sc.channel_index = 1 THEN sc.file_name ELSE NULL END) AS ch_2_path,
MAX(CASE WHEN sc.channel_index = 2 THEN sc.file_name ELSE NULL END) AS ch_3_path


FROM animal a
INNER JOIN scan_run sr ON a.prep_id = sr.prep_id
INNER JOIN slide s ON sr.id = s.scan_run_id
INNER JOIN slide_czi_to_tif sc ON s.id = sc.slide_id
WHERE a.prep_id = 'DK39' AND s.slide_status = 'Good' and sc.active = 1 
-- and s.id = 2281
GROUP BY s.slide_physical_id, sc.scene_number
ORDER BY s.slide_physical_id, sc.scene_number

