
select * from engine_label el where el.task_id = 41;
select * from engine_labeledshape;

select * from engine_job ej 
where ej.id = 30;





select el.frame,elab.name, el.points, el.job_id 
                from engine_labeledshape el  
                left join engine_label elab on el.label_id = elab.id
                left join engine_job ej on el.job_id = ej.id
                where elab.task_id = 41 
                -- and el.frame = 17
                -- and elab.name = 'infrahypoglossal'
                order by el.frame;

select *
from engine_label elab
left join engine_labeledshape el on elab.id = el.label_id 
where elab.task_id = 42;
               
select *
from engine_job ej where id = 31;
select *
from engine_segment es
where es.task_id = 41;
select *
from engine_task et where id = 41; 
               
select   
layer, group_concat( concat(x,',',y) ) as coords, section
from layer_data
where prep_id  = 'DK52'
and layer = 'Premotor'
group by section
order by section;

select *
from layer_data ld
where 1=1
-- and structure_id >= 52
and prep_id = 'DK52'
and layer = 'PremotorShape';

order by layer,section;



alter table layer_data drop constraint FK__LDA_TID;
alter table layer_data drop index K__LDA_TID;
alter table layer_data drop column transformation_id;
alter table layer_data drop column annotation_type;
delete from layer_data where prep_id = 'DK52' and layer = 'PremotorShape';
alter table layer_data add column segment_id int(11) after section;
select distinct ld.prep_id, ld.layer, ld.input_type_id, it.*
from layer_data ld
inner join input_type it on ld.input_type_id = it.id
order by ld.prep_id, ld.layer, ld.input_type_id;

select * from neuroglancer_urls nu where id = 307;

select * 
from auth_user au where id = 16;



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
                                                                                                
