drop table if exists transformation;

CREATE TABLE `transformation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prep_id` varchar(20) NOT NULL,
  `person_id` int(11) NOT NULL,
  `input_type` enum('manual','detected','aligned') NOT NULL DEFAULT 'manual',
  `com_name` varchar(50) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `created` datetime(6) NOT NULL,
  `updated` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `K__T_AID` (`prep_id`),
  KEY `K__T_PID` (`person_id`),
  KEY `K__T_INID` (`input_type`),
  UNIQUE KEY `UK__T_AID_PID_INID` (`prep_id`,`person_id`,`input_type`),
  CONSTRAINT `FK__T_PID` FOREIGN KEY (`person_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `FK__T_prep_id` FOREIGN KEY (`prep_id`) REFERENCES `animal` (`prep_id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

alter table center_of_mass add column transformation_id int(11) after person_id;
alter table center_of_mass ADD INDEX `K__COM_TID` (`transformation_id`);
ALTER TABLE center_of_mass ADD CONSTRAINT FK__COM_TID FOREIGN KEY (transformation_id) REFERENCES transformation(id);

