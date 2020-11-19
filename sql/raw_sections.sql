drop table if exists raw_sections;
drop table if exists raw_section;



create table raw_section (
id int(11) NOT NULL AUTO_INCREMENT,
prep_id varchar(200) NOT NULL,
section_number int not null,
channel int not null,
source_file varchar(200) not null,
destination_file varchar(200) not null,
file_status enum('unusable', 'blurry', 'good') not null default 'good',
active tinyint(4) NOT NULL DEFAULT '1',
created timestamp NULL DEFAULT CURRENT_TIMESTAMP,
PRIMARY KEY (id),
KEY K__raw_section_prep_id (prep_id),
CONSTRAINT UK__raw_section_prep_number_channel UNIQUE (prep_id, section_number, channel),
CONSTRAINT FK__raw_section_prep_id FOREIGN KEY (prep_id) REFERENCES animal (prep_id)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

