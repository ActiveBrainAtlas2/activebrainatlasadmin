ALTER TABLE __file_operation ADD CONSTRAINT FK__FO_rs_id foreign key (id) references raw_section(id) on update cascade on delete cascade;
