desc marked_cells; 
-- marked cells modification
alter table marked_cells modify column source varchar(25);
update marked_cells set source='UNMARKED' where source = 'NULL';
alter table marked_cells modify column source enum('MACHINE_SURE','MACHINE_UNSURE','HUMAN_POSITIVE','HUMAN_NEGATIVE','UNMARKED') NOT NULL;
update marked_cells set FK_cell_type_id = 26 where FK_cell_type_id is null;
-- annotation session 
ALTER TABLE `annotation_session` ADD INDEX `K__annotation_type_active` (`active`, `annotation_type`);
update annotation_session set active=0 where active is null;
alter table annotation_session modify active tinyint(1) not null default 0;
-- finish updates