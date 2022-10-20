truncate marked_cells;
select * from marked_cells mc; 

select au.username ,s.*, as2.*
from marked_cells mc
inner join annotation_session as2 on mc.FK_session_id = as2.id 
inner join auth_user au on as2.FK_annotator_id = au.id 
inner join structure s on as2.FK_structure_id = s.id 
where (mc.FK_cell_type_id is null OR as2.);

desc marked_cells;
alter table marked_cells modify column source varchar(25);
update marked_cells set source='UNMARKED' where source = 'NULL';
alter table marked_cells modify column source enum('MACHINE_SURE','MACHINE_UNSURE','HUMAN_POSITIVE','HUMAN_NEGATIVE','UNMARKED') NOT NULL;
update marked_cells set FK_cell_type_id = 26 where FK_cell_type_id is null;

ALTER TABLE `annotation_session` ADD INDEX `K__active` (`active`);
ALTER TABLE `annotation_session` ADD INDEX `K__annotation_type` (`annotation_type`);
ALTER TABLE `annotation_session` ADD INDEX `K__annotation_type_active` (`active`, `annotation_type`);

explain SELECT id, FK_prep_id, FK_structure_id, 
FK_annotator_id, created, annotation_type, 
FK_parent, active 
FROM annotation_session
WHERE active = 1 
AND annotation_type = 'MARKED_CELL'
ORDER BY 
FK_prep_id ASC, 
annotation_session.annotation_type ASC, 
annotation_session.FK_annotator_id ASC
;
show create table annotation_session;
CREATE TABLE annotation_session (
  id int(11) NOT NULL AUTO_INCREMENT,
  created timestamp NOT NULL DEFAULT current_timestamp(),
  annotation_type enum('POLYGON_SEQUENCE','MARKED_CELL','STRUCTURE_COM') DEFAULT NULL,
  FK_annotator_id int(11) NOT NULL,
  FK_prep_id varchar(20) NOT NULL,
  FK_parent int(11) NOT NULL COMMENT 'SELF-REFERENCES id [IN THIS TABLE]',
  FK_structure_id int(11) NOT NULL COMMENT 'TABLE structure SHOULD ONLY CONTAIN BIOLOGICAL STRUCTURES',
  active tinyint(1) DEFAULT 0,
  PRIMARY KEY (id),
  KEY FK_annotator_id (FK_annotator_id),
  KEY FK_prep_id (FK_prep_id),
  KEY FK_structure_id (FK_structure_id),
  CONSTRAINT annotation_session_ibfk_1 FOREIGN KEY (FK_annotator_id) REFERENCES auth_user (id),
  CONSTRAINT annotation_session_ibfk_2 FOREIGN KEY (FK_prep_id) REFERENCES animal (prep_id),
  CONSTRAINT annotation_session_ibfk_3 FOREIGN KEY (FK_structure_id) REFERENCES structure (id)
) ENGINE=InnoDB AUTO_INCREMENT=6983 DEFAULT CHARSET=utf8mb3