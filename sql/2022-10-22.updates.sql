truncate marked_cells;
SELECT `annotation_session`.`active`, `annotation_session`.`created`, `annotation_session`.`id`, 
`annotation_session`.`FK_prep_id`, `annotation_session`.`FK_structure_id`, `annotation_session`.`FK_annotator_id`, 
`annotation_session`.`annotation_type`, `annotation_session`.`FK_parent` 
FROM `annotation_session` 
WHERE (`annotation_session`.`FK_prep_id` = 'DK41' 
AND `annotation_session`.`FK_structure_id` = 52 
AND `annotation_session`.`FK_annotator_id` = 38 
AND `annotation_session`.`annotation_type` = 'MARKED_CELL' AND `annotation_session`.`active`);


select as2.id, mc.source, ct.cell_type 
from marked_cells mc
inner join annotation_session as2 on mc.FK_session_id = as2.id 
inner join cell_type ct on mc.FK_cell_type_id = ct.id 
where as2.FK_prep_id = 'DK41' 
and as2.FK_structure_id = 52
and as2.FK_annotator_id = 38
and as2.annotation_type = 'MARKED_CELL'
and mc.source = 'HUMAN_NEGATIVE' and ct.cell_type  = 'mixed'
order by mc.source, ct.cell_type; 

SELECT `marked_cells`.`FK_session_id`, `marked_cells`.`source`, `marked_cells`.`FK_cell_type_id` 
FROM `marked_cells` 
INNER JOIN `annotation_session` ON (`marked_cells`.`FK_session_id` = `annotation_session`.`id`) 
INNER JOIN `cell_type` ON (`marked_cells`.`FK_cell_type_id` = `cell_type`.`id`) 
WHERE (`annotation_session`.`FK_prep_id` = 'DK41' 
AND `annotation_session`.`FK_structure_id` = 52 
AND `annotation_session`.`FK_annotator_id` = 38 
AND `annotation_session`.`annotation_type` = 'MARKED_CELL' 
AND `annotation_session`.`active` AND `cell_type`.`cell_type` = 'mixed');

select mc.FK_session_id, mc.source, ct.cell_type, as2.annotation_type , as2.FK_parent  
from marked_cells mc 
inner join annotation_session as2 on mc.FK_session_id = as2.id 
left join cell_type ct on mc.FK_cell_type_id = ct.id 
order by as2.created;

select * from marked_cells mc; 



-- marked cells modification
alter table marked_cells modify column source varchar(25);
update marked_cells set source='UNMARKED' where source = 'NULL';
alter table marked_cells modify column source enum('MACHINE_SURE','MACHINE_UNSURE','HUMAN_POSITIVE','HUMAN_NEGATIVE','UNMARKED') NOT NULL;
update marked_cells set FK_cell_type_id = 26 where FK_cell_type_id is null;
-- annotation session 
ALTER TABLE `annotation_session` ADD INDEX `K__annotation_type_active` (`active`, `annotation_type`);
-- finish updates
select * from annotation_session as2 where id = 4058;
desc animal; 
truncate table background_task;
truncate table background_task_completedtask; 
truncate table marked_cells; 