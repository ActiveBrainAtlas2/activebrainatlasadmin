-- begin archive set updates
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

