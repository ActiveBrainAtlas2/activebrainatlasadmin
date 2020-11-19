drop procedure if exists create_sections;


DELIMITER ;;
CREATE DEFINER=`dklab`@`%` PROCEDURE `create_sections`(
IN PREPID varchar(20),
IN ORDERBY varchar(5)
)
BEGIN

SET @query = CONCAT("DELETE FROM section WHERE prep_id = '", PREPID, "'");
PREPARE stmt FROM @query;
EXECUTE stmt;

SET @query = CONCAT("DELETE FROM raw_section WHERE prep_id = '", PREPID, "'");
PREPARE stmt FROM @query;
EXECUTE stmt;

SET @rownum = 0;


SET @query = CONCAT("INSERT INTO section (prep_id, slide_id, tif_id, slide_physical_id, scene_number, file_name, section_qc, ch_1_path, ch_2_path, ch_3_path, ch_4_path)
SELECT
a.prep_id,
s.id,
sc.id,
s.slide_physical_id,
sc.scene_number,
CONCAT(a.prep_id, '_',
LPAD(
@rownum := @rownum + 1,

4,'0'),'.tif') as file_name,
'OK' as section_qc,
MAX(CASE WHEN sc.channel_index = 0 THEN sc.file_name ELSE NULL END) AS ch_1_path,
MAX(CASE WHEN sc.channel_index = 1 THEN sc.file_name ELSE NULL END) AS ch_2_path,
MAX(CASE WHEN sc.channel_index = 2 THEN sc.file_name ELSE NULL END) AS ch_3_path,
MAX(CASE WHEN sc.channel_index = 3 THEN sc.file_name ELSE NULL END) AS ch_4_path

FROM animal a
INNER JOIN scan_run sr ON a.prep_id = sr.prep_id
INNER JOIN slide s ON sr.id = s.scan_run_id
INNER JOIN slide_czi_to_tif sc ON s.id = sc.slide_id
WHERE a.prep_id = '", PREPID, "'
 AND s.slide_status = 'Good'
 and sc.active = 1
GROUP BY s.slide_physical_id, sc.scene_number
ORDER BY s.slide_physical_id, sc.scene_number ");


PREPARE stmt FROM @query;
EXECUTE stmt;

SET @rownum = 0;

SET @query = CONCAT("
insert into raw_section (prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)

select 
a.prep_id,
@rownum := @rownum + 1 AS section_number,
sc.id AS tif_id,
s.slide_physical_id,
sc.scene_number,
sc.channel,
sc.file_name as source_file,
CONCAT(a.prep_id,'_ID_',
LPAD(@rownum,4,0),
'_slide',lpad(s.slide_physical_id,3,0),'_S',sc.scene_number,'_C',sc.channel,'.tif') as destination_file,
'good' as file_status,
sc.active,
sc.created
FROM animal a
INNER JOIN scan_run sr ON a.prep_id = sr.prep_id
INNER JOIN slide s ON sr.id = s.scan_run_id
INNER JOIN slide_czi_to_tif sc ON s.id = sc.slide_id
WHERE a.prep_id = '", PREPID, "'
AND s.slide_status = 'Good'
AND sc.active = 1
ORDER BY s.slide_physical_id, sc.scene_number, sc.channel
");


PREPARE stmt FROM @query;
EXECUTE stmt;



END ;;
DELIMITER ;
