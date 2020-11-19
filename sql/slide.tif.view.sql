drop view if exists slide_view;

create view slide_view as
select a.prep_id,

sc.file_name,sc.section_number,sc.scene_index,sc.channel,sc.active

FROM animal a
INNER JOIN scan_run sr ON a.prep_id = sr.prep_id
INNER JOIN slide s ON sr.id = s.scan_run_id
INNER JOIN slide_czi_to_tif sc ON s.id = sc.slide_id


where s.slide_status = 'Good';
