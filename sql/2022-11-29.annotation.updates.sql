-- archiving modification start
alter table annotations_point_archive drop column prep_id;
alter table annotations_point_archive drop column FK_structure_id;
alter table annotations_point_archive drop column FK_owner_id;
-- alter table annotations_point_archive drop column FK_archive_set_id;
alter table annotations_point_archive drop column FK_input_id;
alter table annotations_point_archive drop column label;
delete from annotations_point_archive where FK_session_id is null;
alter table annotations_point_archive modify column FK_session_id int(11) not null;


-- delete from annotations_point_archive where FK_session_id in (select id from annotation_session);
-- move inactive data from the 3 tables into the archive
-- fill up archive with inactive marked cells
-- insert into annotations_point_archive (x, y, z, source, FK_session_id, FK_cell_type_id)
-- select mc.x, mc.y, mc.z, mc.source, as2.id as FK_session_id, mc.FK_cell_type_id  
-- from marked_cells mc 
-- inner join annotation_session as2 on mc.FK_session_id = as2.id
-- where as2.active = 0;
-- delete MC 
-- from marked_cells MC 
-- inner join annotation_session as2 on MC.FK_session_id = as2.id
-- and as2.active = 0;
-- TODO fill up archive with inactive polygon_sequences data
-- TODO fill up archive with inactive structure_com data
-- end archiving updates
