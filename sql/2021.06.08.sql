DROP TABLE IF EXISTS layer_data_combo;

CREATE TABLE `layer_data_combo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url_id` int(11) DEFAULT NULL,
  `prep_id` varchar(20) NOT NULL,
  `structure_id` int(11) NOT NULL,
  `person_id` int(11) NOT NULL,
  `input_type_id` int(11) NOT NULL DEFAULT 1,
  `transformation_id` int(11) DEFAULT NULL,
  `layer` varchar(255) DEFAULT NULL,
  `x` float DEFAULT NULL,
  `y` float DEFAULT NULL,
  `section` int(11) NOT NULL DEFAULT 0,
  `active` tinyint(1) DEFAULT NULL,
  `created` datetime(6) NOT NULL,
  `updated` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `K__LDA_URLID` (`url_id`),
  KEY `K__LDA_AID` (`prep_id`),
  KEY `K__LDA_SID` (`structure_id`),
  KEY `K__LDA_PID` (`person_id`),
  KEY `K__LDA_ITID` (`input_type_id`),
  KEY `K__LDA_TID` (`transformation_id`),
  CONSTRAINT `FK__LDA_URLID` FOREIGN KEY (`url_id`) REFERENCES `neuroglancer_urls` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `FK__LDA_AID` FOREIGN KEY (`prep_id`) REFERENCES `animal` (`prep_id`) ON UPDATE CASCADE,
  CONSTRAINT `FK__LDA_STRID` FOREIGN KEY (`structure_id`) REFERENCES `structure` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `FK__LDA_PID` FOREIGN KEY (`person_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `FK__LDA_ITID` FOREIGN KEY (`input_type_id`) REFERENCES `com_type` (`id`),
  CONSTRAINT `FK__LDA_TID` FOREIGN KEY (`transformation_id`) REFERENCES `transformation` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;



insert into layer_data_combo 
(url_id, prep_id, structure_id, person_id,input_type_id,layer,x,y,section,active,created,updated)
select ld.url_id, ld.prep_id, 52 as structure_id,
nu.person_id as person_id,
1 as input_type_id,
ld.layer,ld.x,ld.y,ld.section,ld.active,ld.created,ld.updated
from layer_data ld
inner join neuroglancer_urls nu on ld.url_id = nu.id; 

insert into layer_data_combo 
(transformation_id, prep_id, structure_id, person_id,input_type_id,layer,x,y,section,active,created,updated)
select transformation_id ,
prep_id, structure_id,
person_id,
input_type_id,
'COM' as layer,x,y,section,active,created,updated
from center_of_mass;

drop table if exists layer_data;
rename table layer_data_combo to layer_data;

