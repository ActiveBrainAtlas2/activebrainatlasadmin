alter table marked_cells modify column x decimal(8,2) not null default 0;
alter table marked_cells modify column y decimal(8,2) not null default 0;
alter table marked_cells modify column z decimal(8,2) not null default 0;

alter table polygon_sequences  modify column x decimal(8,2) not null default 0;
alter table polygon_sequences  modify column y decimal(8,2) not null default 0;
alter table polygon_sequences  modify column z decimal(8,2) not null default 0;

alter table structure_com  modify column x decimal(8,2) not null default 0;
alter table structure_com  modify column y decimal(8,2) not null default 0;
alter table structure_com  modify column z decimal(8,2) not null default 0;

drop table if exists marked_cells_tmp;
create table marked_cells_tmp AS
select source, x, y, z, FK_session_id , FK_cell_type_id 
from marked_cells mc 
group by source, x, y, z, FK_session_id , FK_cell_type_id
order by source, x, y, z, FK_session_id , FK_cell_type_id;
truncate table marked_cells;
insert into marked_cells (source, x, y, z, FK_session_id , FK_cell_type_id)
select source, x, y, z, FK_session_id , FK_cell_type_id
from marked_cells_tmp;
ALTER TABLE marked_cells ADD CONSTRAINT UK_session_xyz UNIQUE (FK_session_id, x, y, z);
