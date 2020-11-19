
--
-- Table structure for table `structure`
--

DROP TABLE IF EXISTS `structure`;
CREATE TABLE `structure` (
id int(11) not null auto_increment,
  `abbreviation` varchar(25) NOT NULL,
  `description` longtext NOT NULL,
  `color` int(11) NOT NULL DEFAULT 100,
  `hexadecimal` char(7) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

--
-- Dumping data for table `structure`
--


INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('10N_L','Dorsal nucleus of vagus nerve',1,'#0CFF95',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('10N_R','Dorsal nucleus of vagus nerve',1,'#0CFF95',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('12N','Hypoglossal nucleus',2,'#FF3578',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('3N_L','Oculomotor nucleus',3,'#FF8E6B',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('3N_R','Oculomotor nucleus',3,'#FF8E6B',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('4N_L','Trochlear nucleus',4,'#C6FF6B',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('4N_R','Trochlear nucleus',4,'#C6FF6B',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('5N_L','Trigeminal motor nucleus',5,'#FFDA45',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('5N_R','Trigeminal motor nucleus',5,'#FFDA45',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('6N_L','Abducens nucleus',6,'#0CFF95',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('6N_R','Abducens nucleus',6,'#0CFF95',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('7N_L','Facial nucleus',7,'#7633FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('7N_R','Facial nucleus',7,'#7633FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('7n_L','Facial nerve',9,'#FF1B09',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('7n_R','Facial nerve',9,'#FF1B09',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('AP','Area postrema',28,'#5E80FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Amb_L','Nucleus ambiggus',8,'#4EFF45',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Amb_R','Nucleus ambiggus',8,'#4EFF45',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('DC_L','Dorsal cochlea nucleus',10,'#2FD5FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('DC_R','Dorsal cochlea nucleus',10,'#2FD5FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('IC','Inferior colliculus',11,'#F66EFF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('LC_L','Locus corelus',12,'#6C96FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('LC_R','Locus corelus',12,'#6C96FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('LRt_L','Lateral reticular nucleus',13,'#FF0BE5',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('LRt_R','Lateral reticular nucleus',13,'#FF0BE5',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('PBG_L','Parabigeminal nucleus',14,'#1EFF29',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('PBG_R','Parabigeminal nucleus',14,'#1EFF29',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Pn_L','Pontine grey',15,'#FFE031',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Pn_R','Pontine grey',15,'#FFE031',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Pr5','Trigeminal Principalis \r\nCombination of Pr5	Pr5DM	Pr5VL',255,'#FFFFFF',0, NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('R','Red nucleus',16,'#FF8E6B',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('RtTg','Reticulotegmental nucleus',17,'#9BFF0B',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('SC','Superior colliculus',18,'#22D8FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('SNC_L','Substantia niagra, compact',19,'#32FF32',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('SNC_R','Substantia niagra, compact',19,'#32FF32',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('SNR_L','Substantia niagra, reticular',20,'#7490EF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('SNR_R','Substantia niagra, reticular',20,'#7490EF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Sp5C_L','Spinal-trigeminal nucleus, caudalis',21,'#2FD5FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Sp5C_R','Spinal-trigeminal nucleus, caudalis',21,'#2FD5FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Sp5I_L','Spinal-trigeminal nucleus, interpolaris',22,'#42E2FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Sp5I_R','Spinal-trigeminal nucleus, interpolaris',22,'#42E2FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Sp5O_L','Spinal-trigeminal nucleus, oralis',23,'#F369FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Sp5O_R','Spinal-trigeminal nucleus, oralis',23,'#F369FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Tz_L','Nucleus of trapezoidal body',24,'#78FFCB',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('Tz_R','Nucleus of trapezoidal body',24,'#78FFCB',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('VCA_L','Ventral cochlea nucleus, anterior',25,'#FF417B',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('VCA_R','Ventral cochlea nucleus, anterior',25,'#FF417B',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('VCP_L','Ventral cochlea nucleus, posterior',26,'#B6FF58',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('VCP_R','Ventral cochlea nucleus, posterior',26,'#B6FF58',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('VLL_L','Ventral lateral lemniscus',27,'#A144FF',1,NOW());
INSERT INTO `structure` (abbreviation,description, color, hexadecimal, active,created) VALUES ('VLL_R','Ventral lateral lemniscus',27,'#A144FF',1,NOW());
