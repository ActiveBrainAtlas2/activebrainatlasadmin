
--
-- Table structure for table `journals`
--

DROP TABLE IF EXISTS `journals`;
CREATE TABLE `journals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prep_id` varchar(20) NOT NULL,
  `entry` longtext NOT NULL,
  `created` timestamp NOT NULL DEFAULT current_timestamp(),
  `active` tinyint(4) NOT NULL DEFAULT 1,
  `completed` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `K__journals_prep_id` (`prep_id`),
  CONSTRAINT `FK__journals_prep_id` FOREIGN KEY (`prep_id`) REFERENCES `animal` (`prep_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
