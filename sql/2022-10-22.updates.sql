select *
from elastix_transformation
where prep_id = 'DK52' 
-- and  section in ('005','006','007')
order by metric;

select resolution , zresolution 
FROM scan_run WHERE prep_id = 'DK79';

delete from elastix_transformation where prep_id = 'DK79' and section in ('006','007');

UPDATE elastix_transformation SET rotation=0.055, xshift=528, yshift=-160      
WHERE section = '006' and prep_id = 'DK79' LIMIT 1;

UPDATE elastix_transformation SET rotation=-0.13114, xshift=-586.424, yshift=110      
WHERE section = '007' and prep_id = 'DK79' LIMIT 1;

UPDATE elastix_transformation SET rotation=0.301, xshift=-81.579, yshift=-60.87      
WHERE section = '331' and prep_id = 'DK79' LIMIT 1;



-- -0.75 too much clockwise, -0.5 too much, -0.25 too much, 0, almost
-- xshift -81 too far right
UPDATE elastix_transformation SET rotation=-0.124173, xshift=-70, yshift=-25      
WHERE section = '332' and prep_id = 'DK79' LIMIT 1;

UPDATE elastix_transformation SET rotation=0.1, xshift=250.0, yshift=-65.0      
WHERE section = '332' and prep_id = 'DK79' LIMIT 1;
