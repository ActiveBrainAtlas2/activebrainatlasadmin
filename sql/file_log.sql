
--
-- Table structure for table file_log
--

DROP TABLE IF EXISTS file_log;
CREATE TABLE file_log (
  id int(11) NOT NULL AUTO_INCREMENT,
  prep_id varchar(20) NOT NULL,
  progress_id int(11) NOT NULL,
  filename varchar(255) NOT NULL,
  active tinyint(1) NOT NULL DEFAULT 1,
  created timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  UNIQUE KEY UK__AID_PID_C_S (prep_id,progress_id, filename),
  KEY K__FILE_LOG_AID (prep_id),
  KEY K__FILE_LOG_PID (progress_id),
  CONSTRAINT FK__FILE_LOG_AID FOREIGN KEY (prep_id) REFERENCES animal (prep_id) ON UPDATE CASCADE,
  CONSTRAINT FK__FILE_LOG_PID FOREIGN KEY (progress_id) REFERENCES progress_lookup (id) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
