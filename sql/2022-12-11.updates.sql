alter table annotation_session add column FK_state_id int(11) default null after FK_prep_id;
alter table annotation_session drop column FK_parent;

delete from annotation_session 
where id NOT in (
select distinct FK_session_id
from marked_cells
union
select distinct FK_session_id
from polygon_sequences
union
select distinct FK_session_id 
from structure_com);
