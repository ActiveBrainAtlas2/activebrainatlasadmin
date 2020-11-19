select rs.section_number, rs.channel, sc.channel, sc.channel_index, sc.file_name
from slide s
inner join slide_czi_to_tif sc on s.id=sc.slide_id
inner join raw_section rs on sc.id=rs.tif_id
where rs.prep_id = 'DK52'
order by rs.section_number, rs.channel
limit 50;
