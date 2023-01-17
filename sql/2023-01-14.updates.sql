drop table if exists ps_tmp;
create table ps_tmp AS
select source, x, y, z, FK_session_id , polygon_index, point_order  
from polygon_sequences ps  
group by source, x, y, z, FK_session_id , polygon_index, point_order
order by source, x, y, z, FK_session_id , polygon_index, point_order;
truncate table polygon_sequences;
insert into polygon_sequences (source, x, y, z, FK_session_id , polygon_index, point_order)
select source, x, y, z, FK_session_id , polygon_index, point_order
from ps_tmp;
drop table if exists ps_tmp;
ALTER TABLE polygon_sequences ADD CONSTRAINT UK_ps_session_xyz_index UNIQUE (FK_session_id, x, y, z, polygon_index, point_order);

-- new updates on structure_com
ALTER TABLE structure_com  ADD CONSTRAINT UK_sc_session_xyz UNIQUE (source, x, y, z, FK_session_id);

