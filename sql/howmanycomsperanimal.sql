select s.abbreviation as Structures,
count(distinct ld.prep_id) as 'Instances',
sum(CASE WHEN ld.prep_id='DK39' THEN 1 ELSE 0 END) AS DK39,
sum(CASE WHEN ld.prep_id='DK41' THEN 1 ELSE 0 END) AS DK41,
sum(CASE WHEN ld.prep_id='DK43' THEN 1 ELSE 0 END) AS DK43,
sum(CASE WHEN ld.prep_id='DK46' THEN 1 ELSE 0 END) AS DK46,
sum(CASE WHEN ld.prep_id='DK52' THEN 1 ELSE 0 END) AS DK52,
sum(CASE WHEN ld.prep_id='DK54' THEN 1 ELSE 0 END) AS DK54,
sum(CASE WHEN ld.prep_id='DK55' THEN 1 ELSE 0 END) AS DK55,
sum(CASE WHEN ld.prep_id='DK63' THEN 1 ELSE 0 END) AS DK63,
sum(CASE WHEN ld.prep_id='MD589' THEN 1 ELSE 0 END) AS MD589
from structure s
left join layer_data ld on ld.structure_id = s.id
where 1=1
and s.active = True
and ld.active  = True
-- and prep_id  in ('DK63')
and ld.input_type_id in (2)
and ld.person_id in (2)
and ld.layer = 'COM'
group by ld.structure_id
order by s.abbreviation;
