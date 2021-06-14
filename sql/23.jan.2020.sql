alter table journals add column url_id int(11);
alter table journals add column section int(11);
alter table journals add column channel int(11);


ALTER TABLE journals ADD CONSTRAINT FK__url_id foreign key (url_id) references neuroglancer_urls(id) on update cascade on delete cascade;
