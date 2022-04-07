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


CREATE TABLE `annotations_point_archive` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prep_id` varchar(20) CHARACTER SET utf8 NOT NULL,
  `FK_structure_id` int(11) NOT NULL,
  `FK_owner_id` int(11) NOT NULL,
  `FK_input_id` int(11) NOT NULL,
  `label` varchar(255) CHARACTER SET utf8 NOT NULL,
  `x` float DEFAULT NULL,
  `y` float DEFAULT NULL,
  `z` float NOT NULL DEFAULT 0,
  `FK_archive_set_id` int(11) DEFAULT NULL,
  `segment_id` char(40) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=91439 DEFAULT CHARSET=utf8mb4




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

ALTER TABLE annotations_points ADD COLUMN ordering INT NOT NULL DEFAULT 0 after segment_id;
ALTER TABLE annotations_point_archive ADD COLUMN ordering INT NOT NULL DEFAULT 0 after segment_id;

ALTER TABLE annotations_points ADD COLUMN volume_id char(40) DEFAULT NULL after segment_id;
ALTER TABLE annotations_point_archive ADD COLUMN volume_id char(40) DEFAULT NULL after segment_id;

ALTER TABLE annotations_points CHANGE segment_id polygon_id char(40);
ALTER TABLE annotations_point_archive CHANGE segment_id polygon_id char(40);
## new table brain_shape
DROP TABLE IF EXISTS brain_shape;
CREATE TABLE `brain_shape` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prep_id` varchar(20) NOT NULL,
  `FK_structure_id` int(11) NOT NULL,
  `created` DATETIME NOT NULL,
  `updated` timestamp NOT NULL DEFAULT current_timestamp(),
  `dimensions` varchar(50) NOT NULL,
  `xoffset` float NOT NULL,
  `yoffset` float NOT NULL,
  `zoffset` float NOT NULL,
  `transformed` tinyint(4) NOT NULL DEFAULT 0,
  `numpy_data` LONGBLOB NOT NULL,
  `active` tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  KEY `K__BS_prep_id` (`prep_id`),
  KEY `K__BS_FK_structure_id` (`FK_structure_id`),
  CONSTRAINT `FK__BS_prep_id` FOREIGN KEY (`prep_id`) REFERENCES `animal` (`prep_id`) ON UPDATE CASCADE,
  CONSTRAINT `FK__BS_FK_structure_id` FOREIGN KEY (`FK_structure_id`) REFERENCES `structure` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `animal` (
  `prep_id` varchar(20) NOT NULL COMMENT 'Name for lab mouse/rat, max 20 chars',
  `performance_center` enum('CSHL','Salk','UCSD','HHMI','Duke') DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL COMMENT 'the mouse''s date of birth',
  `species` enum('mouse','rat') DEFAULT NULL,
  `strain` varchar(50) DEFAULT NULL,
  `sex` enum('M','F') DEFAULT NULL COMMENT '(M/F) either ''M'' for male, ''F'' for female',
  `genotype` varchar(100) DEFAULT NULL COMMENT 'transgenic description, usually "C57"; We will need a genotype table',
  `breeder_line` varchar(100) DEFAULT NULL COMMENT 'We will need a local breeding table',
  `vender` enum('Jackson','Charles River','Harlan','NIH','Taconic') DEFAULT NULL,
  `stock_number` varchar(100) DEFAULT NULL COMMENT 'if not from a performance center',
  `tissue_source` enum('animal','brain','slides') DEFAULT NULL,
  `ship_date` date DEFAULT NULL,
  `shipper` enum('FedEx','UPS') DEFAULT NULL,
  `tracking_number` varchar(100) DEFAULT NULL,
  `aliases_1` varchar(100) DEFAULT NULL COMMENT 'names given by others',
  `aliases_2` varchar(100) DEFAULT NULL,
  `aliases_3` varchar(100) DEFAULT NULL,
  `aliases_4` varchar(100) DEFAULT NULL,
  `aliases_5` varchar(100) DEFAULT NULL,
  `comments` varchar(2001) DEFAULT NULL COMMENT 'assessment',
  `active` tinyint(4) NOT NULL DEFAULT 1,
  `created` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`prep_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


ALTER TABLE animal DROP PRIMARY KEY;
ALTER TABLE animal ADD COLUMN id int(11) auto_increment primary key first;

