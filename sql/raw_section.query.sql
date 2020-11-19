
select count(*)

from raw_section rs
inner join slide_czi_to_tif st on rs.tif_id = st.id
inner join slide s on st.slide_id = s.id
WHERE rs.prep_id = 'DK52'
-- AND rs.channel = 1
;
