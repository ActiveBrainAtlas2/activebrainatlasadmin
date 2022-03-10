DROP TABLE IF EXISTS annotations_points;
DROP TABLE IF EXISTS archive_set;
CREATE TABLE archive_set (
id int not null primary key auto_increment,
prep_id varchar(20) CHARACTER SET utf8 NOT NULL,
FK_input_id int(11) NOT NULL,
label varchar(255) CHARACTER SET utf8 NOT NULL,
FK_parent int not null,
created datetime(6) not null,
FK_update_user_id int not null,
KEY `K__AS_UUID` (`FK_update_user_id`),
CONSTRAINT `FK__AS_PID` FOREIGN KEY (`FK_update_user_id`) REFERENCES `auth_user` (`id`)
);

RENAME TABLE layer_data TO annotations_points;
-- remove foreign keys
  ALTER TABLE annotations_points DROP FOREIGN KEY `FK__LDA_AID`;
  ALTER TABLE annotations_points DROP FOREIGN KEY `FK__LDA_ITID` ;
  ALTER TABLE annotations_points DROP FOREIGN KEY`FK__LDA_PID` ;
  ALTER TABLE annotations_points DROP FOREIGN KEY`FK__LDA_STRID` ;
-- remove indexes
  DROP INDEX `K__LDA_AID` ON annotations_points;
  DROP INDEX `K__LDA_SID` ON annotations_points;
  DROP INDEX `K__LDA_PID` ON annotations_points;
  DROP INDEX `K__LDA_ITID` ON annotations_points;
-- rename columns
 ALTER TABLE annotations_points CHANGE structure_id FK_structure_id int(11) NOT NULL;
 ALTER TABLE annotations_points CHANGE person_id FK_owner_id int(11) NOT NULL;
 ALTER TABLE annotations_points CHANGE input_type_id  FK_input_id int(11) NOT NULL;
 ALTER TABLE annotations_points CHANGE layer label varchar(255) NOT NULL;
 ALTER TABLE annotations_points CHANGE section z float NOT NULL default 0.0;
-- drop columns
ALTER TABLE annotations_points DROP COLUMN vetted;
-- add indexes
ALTER TABLE annotations_points ADD INDEX `K__AP_AID` (`prep_id`);
ALTER TABLE annotations_points ADD INDEX `K__AP_BRID` (`FK_structure_id`);
ALTER TABLE annotations_points ADD INDEX `K__AP_OID` (`FK_owner_id`);
ALTER TABLE annotations_points ADD INDEX `K__AP_ITID` (`FK_input_id`);
-- add FKs
ALTER TABLE annotations_points ADD CONSTRAINT `FK__AP_AID` FOREIGN KEY (`prep_id`) 
REFERENCES animal(`prep_id`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE annotations_points ADD CONSTRAINT `FK__AP_BRID` FOREIGN KEY (`FK_structure_id`) 
REFERENCES structure(`id`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE annotations_points ADD CONSTRAINT `FK__AP_OID` FOREIGN KEY (`FK_owner_id`) 
REFERENCES auth_user(`id`) ON UPDATE CASCADE ON DELETE CASCADE;

ALTER TABLE annotations_points ADD CONSTRAINT `FK__AP_ITID` FOREIGN KEY (`FK_input_id`) 
REFERENCES com_type(`id`) ON UPDATE CASCADE ON DELETE CASCADE;
DROP TABLE IF EXISTS annotations_point_archive;
CREATE TABLE annotations_point_archive AS
SELECT prep_id, FK_structure_id ,FK_owner_id, FK_input_id,label, x, y, z
FROM annotations_points ap 
WHERE ap.active = 0
ORDER BY prep_id, FK_structure_id ,FK_owner_id, FK_input_id,label, x, y, z;
ALTER TABLE annotations_point_archive ADD id INT PRIMARY KEY AUTO_INCREMENT FIRST;
ALTER TABLE annotations_point_archive ADD FK_archive_set_id INT;


DELETE FROM annotations_points wHERE active = 0;
ALTER TABLE annotations_points DROP COLUMN updated_by;
ALTER TABLE annotations_points DROP COLUMN created;
ALTER TABLE annotations_points DROP COLUMN updated;
# new column
ALTER TABLE annotations_points ADD COLUMN segment_id char(40) DEFAULT NULL;
ALTER TABLE annotations_point_archive ADD COLUMN segment_id char(40) DEFAULT NULL;
INSERT INTO structure (id, abbreviation, description,color, hexadecimal,active, created, is_structure) 
values (54, 'polygon','Brain region drawn by anatomist',300,'#FFF000',1,NOW(), 0);


