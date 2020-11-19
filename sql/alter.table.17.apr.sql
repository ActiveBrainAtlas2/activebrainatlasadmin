alter table animal drop column section_direction;
alter table histology modify column side_sectioned_first enum('left','right','ASC','DESC') not null default 'ASC';
update histology set side_sectioned_first = 'ASC' where side_sectioned_first = 'left';
alter table histology modify column side_sectioned_first enum('ASC','DESC') not null default 'ASC';
