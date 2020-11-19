-- alter table raw_section drop column destination_file;

--
-- Table structure for table `__file_operation`
--

DROP TABLE IF EXISTS `__file_operation`;
CREATE TABLE `__file_operation` (
  `id` int(11) NOT NULL,
  `file_name` varchar(200) NOT NULL,
  `thumbnail` tinyint(4) NOT NULL,
  `czi_to_tif` tinyint(4) NOT NULL,
  `histogram` tinyint(4) NOT NULL,
  `processing_duration` float NOT NULL,
  `created` datetime NOT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `FK__FO_RS_ID` FOREIGN KEY (`id`) REFERENCES `raw_section` (`id`) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
