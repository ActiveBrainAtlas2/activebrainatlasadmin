-- marked cells modification
alter table marked_cells modify column source varchar(25);
update marked_cells set source='UNMARKED' where source = 'NULL';
alter table marked_cells modify column source enum('MACHINE_SURE','MACHINE_UNSURE','HUMAN_POSITIVE','HUMAN_NEGATIVE','UNMARKED') NOT NULL;
update marked_cells set FK_cell_type_id = 26 where FK_cell_type_id is null;
-- annotation session 
ALTER TABLE `annotation_session` ADD INDEX `K__annotation_type_active` (`active`, `annotation_type`);
update annotation_session set active=0 where active is null;
alter table annotation_session modify active tinyint(1) not null default 0;
-- finish marked cell updates

-- begin archive set updates
truncate table archive_set;
alter table archive_set add column FK_session_id int(11) not null after id;
alter table archive_set add column active tinyint(4) not null;
alter table archive_set modify column created datetime(6) not null after FK_update_user_id;
alter table archive_set drop column prep_id;
alter table archive_set drop column FK_input_id;
alter table archive_set drop column label;
alter table archive_set drop column FK_parent;
alter table archive_set drop foreign key FK__AS_PID;
alter table archive_set drop index K__AS_UUID;
alter table archive_set drop column FK_update_user_id;
-- end archive set updates

-- start annotations_point_archive modifications
drop table if exists annotations_point_archive_backup;
CREATE TABLE annotations_point_archive_backup AS SELECT * FROM annotations_point_archive;
truncate table annotations_point_archive;
alter table annotations_point_archive drop column prep_id;
alter table annotations_point_archive drop column FK_structure_id;
alter table annotations_point_archive drop column FK_owner_id;
alter table annotations_point_archive drop column FK_input_id;
alter table annotations_point_archive drop column label;
delete from annotations_point_archive where FK_session_id is null;
alter table annotations_point_archive modify column FK_session_id int(11) not null;


