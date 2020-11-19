drop table if exists raw_section_test;



create table raw_section_test as

select 
a.prep_id,
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
WHERE a.prep_id = 'DK39'
AND s.slide_status = 'Good'
AND sc.active = 1
ORDER BY s.slide_physical_id, sc.scene_number;


select 
rs.slide_physical_id, 
rst.slide_physical_id,
rs.scene_number,rs.source_file,rst.source_file

from raw_section rs
inner join raw_section_test rst 
on rs.tif_id = rst.tif_id 
and rs.scene_number = rst.scene_number
and rs.channel = rst.channel
and rs.slide_physical_id = rst.slide_physical_id
and rs.source_file = rst.source_file
where rs.prep_id = 'DK39'
-- and rs.scene_number != rst.scene_number

order by rs.section_number
;
