
select el.frame, el.frame + 200 as section,elab.name, el.points 
from engine_labeledshape el  
inner join engine_label elab on el.label_id = elab.id
where elab.task_id = 41 
and el.frame = 17
and elab.name = 'infrahypoglossal'
order by el.frame;
                                                                                                
select   
layer, group_concat( concat(x,',',y) ) as coords, section
from layer_data
where prep_id  = 'DK52'
and layer = 'Premotor'
group by section
order by section;
                                                                                                
