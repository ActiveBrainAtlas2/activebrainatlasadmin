
--
-- Table structure for table layer_data
--

DROP TABLE IF EXISTS layer_data;
CREATE TABLE layer_data (
  id int(11) NOT NULL AUTO_INCREMENT,
  url_id int(11) DEFAULT NULL,
  layer varchar(255),
  x int not null default 0,
  y int not null default 0,
  section int not null default 0,
  active tinyint(1) DEFAULT NULL,
  created datetime(6) NOT NULL,
  updated timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  KEY K__URLID (url_id),
  CONSTRAINT FK__URLID FOREIGN KEY (url_id) REFERENCES neuroglancer_urls (id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
