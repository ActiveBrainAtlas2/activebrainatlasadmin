
SET @rownum = 0;


select 
@rownum := @rownum + 1 AS SN,
sc.id AS TIFID,
s.slide_physical_id AS SID,
sc.scene_number AS SCN,
sc.channel AS CH,
sc.file_name as 'source_file                        ',
CONCAT(a.prep_id,'_ID_',
LPAD(@rownum,4,0),
'_slide',lpad(s.slide_physical_id,3,0),'_S',sc.scene_number,'_C',sc.channel,'.tif') as destination_file,
sc.active
FROM animal a
INNER JOIN scan_run sr ON a.prep_id = sr.prep_id
INNER JOIN slide s ON sr.id = s.scan_run_id
INNER JOIN slide_czi_to_tif sc ON s.id = sc.slide_id
WHERE a.prep_id = 'DK39'
AND s.slide_status = 'Good'
AND sc.active = 1
and sc.slide_id = 2281
ORDER BY s.slide_physical_id, sc.scene_number, sc.channel
;
