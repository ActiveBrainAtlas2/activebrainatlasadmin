# Below are the table defiitions

##
## Table structure for table animal
##
@schema
class Animal(dj.Manual):
  prep_id varchar(20) NOT NULL COMMENT 'Name for lab mouse/rat, max 20 chars',
  performance_center enum('CSHL','Salk','UCSD','HHMI','Duke') DEFAULT NULL,
  date_of_birth date DEFAULT NULL COMMENT 'the mouse''s date of birth',
  species enum('mouse','rat') DEFAULT NULL,
  strain varchar(50) DEFAULT NULL,
  sex enum('M','F') DEFAULT NULL COMMENT '(M/F) either ''M'' for male, ''F'' for female',
  genotype varchar(100) DEFAULT NULL COMMENT 'transgenic description, usually "C57"; We will need a genotype table',
  breeder_line varchar(100) DEFAULT NULL COMMENT 'We will need a local breeding table',
  vender enum('Jackson','Charles River','Harlan','NIH','Taconic') DEFAULT NULL,
  stock_number varchar(100) DEFAULT NULL COMMENT 'if not from a performance center',
  tissue_source enum('animal','brain','slides') DEFAULT NULL,
  ship_date date DEFAULT NULL,
  shipper enum('FedEx','UPS') DEFAULT NULL,
  tracking_number varchar(100) DEFAULT NULL,
  section_direction enum('ASC','DESC') NOT NULL DEFAULT 'ASC',
  aliases_1 varchar(100) DEFAULT NULL COMMENT 'names given by others',
  aliases_2 varchar(100) DEFAULT NULL,
  aliases_3 varchar(100) DEFAULT NULL,
  aliases_4 varchar(100) DEFAULT NULL,
  aliases_5 varchar(100) DEFAULT NULL,
  comments varchar(2001) DEFAULT NULL COMMENT 'assessment',
  active tinyint(4) NOT NULL DEFAULT 1,
  created timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (prep_id)
)


##
## Table structure for table histology
##
@schema
class histology(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  prep_id varchar(20) NOT NULL,
  virus_id int(11) DEFAULT NULL,
  label_id int(11) DEFAULT NULL,
  performance_center enum('CSHL','Salk','UCSD','HHMI') DEFAULT NULL COMMENT 'default population is from Injection',
  anesthesia enum('ketamine','isoflurane','pentobarbital','fatal plus') DEFAULT NULL,
  perfusion_age_in_days tinyint(3) unsigned NOT NULL DEFAULT 0,
  perfusion_date date DEFAULT NULL,
  exsangination_method enum('PBS','aCSF','Ringers') DEFAULT NULL,
  fixative_method enum('Para','Glut','Post fix') DEFAULT NULL,
  special_perfusion_notes varchar(200) DEFAULT NULL,
  post_fixation_period tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT '(days)',
  whole_brain enum('Y','N') DEFAULT NULL,
  block varchar(200) DEFAULT NULL COMMENT 'if applicable',
  date_sectioned date DEFAULT NULL,
  side_sectioned_first enum('left','right') NOT NULL DEFAULT 'left',
  sectioning_method enum('cryoJane','cryostat','vibratome','optical','sliding microtiome') DEFAULT NULL,
  section_thickness tinyint(3) unsigned NOT NULL DEFAULT 20 COMMENT '(µm)',
  orientation enum('coronal','horizontal','sagittal','oblique') DEFAULT NULL,
  oblique_notes varchar(200) DEFAULT NULL,
  mounting enum('every section','2nd','3rd','4th','5ft','6th') DEFAULT NULL COMMENT 'used to automatically populate Placeholder',
  counterstain enum('thionin','NtB','NtFR','DAPI','Giemsa','Syto41') DEFAULT NULL,
  comments varchar(2001) DEFAULT NULL COMMENT 'assessment',
  created timestamp NOT NULL DEFAULT current_timestamp(),
  active tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  KEY K__histology_virus_id (virus_id),
  KEY K__histology_label_id (label_id),
  KEY K__histology_prep_id (prep_id),
  CONSTRAINT FK__histology_label_id FOREIGN KEY (label_id) REFERENCES organic_label (id) ON UPDATE CASCADE,
  CONSTRAINT FK__histology_prep_id FOREIGN KEY (prep_id) REFERENCES animal (prep_id) ON UPDATE CASCADE,
  CONSTRAINT FK__histology_virus_id FOREIGN KEY (virus_id) REFERENCES virus (id) ON UPDATE CASCADE
)

##
## Table structure for table injection
##
@schema
class injection(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  prep_id varchar(200) NOT NULL,
  label_id int(11) DEFAULT NULL,
  performance_center enum('CSHL','Salk','UCSD','HHMI','Duke') DEFAULT NULL,
  anesthesia enum('ketamine','isoflurane') DEFAULT NULL,
  method enum('iontophoresis','pressure','volume') DEFAULT NULL,
  injection_volume float NOT NULL DEFAULT 0 COMMENT '(nL)',
  pipet enum('glass','quartz','Hamilton','syringe needle') DEFAULT NULL,
  location varchar(20) DEFAULT NULL COMMENT 'examples: muscle, brain region',
  angle varchar(20) DEFAULT NULL,
  brain_location_dv float NOT NULL DEFAULT 0 COMMENT '(mm) dorsal-ventral relative to Bregma',
  brain_location_ml float NOT NULL DEFAULT 0 COMMENT '(mm) medial-lateral relative to Bregma; check if positive',
  brain_location_ap float NOT NULL DEFAULT 0 COMMENT '(mm) anterior-posterior relative to Bregma',
  injection_date date DEFAULT NULL,
  transport_days int(11) NOT NULL DEFAULT 0,
  virus_count int(11) NOT NULL DEFAULT 0,
  comments varchar(2001) DEFAULT NULL COMMENT 'assessment',
  created timestamp NOT NULL DEFAULT current_timestamp(),
  active tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  KEY K__label_id (label_id),
  KEY FK__injection_prep_id (prep_id),
  CONSTRAINT FK__injection_label_id FOREIGN KEY (label_id) REFERENCES organic_label (id) ON UPDATE CASCADE,
  CONSTRAINT FK__injection_prep_id FOREIGN KEY (prep_id) REFERENCES animal (prep_id)
)

##
## Table structure for table injection_virus
##
@schema
class injection_virus(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  injection_id int(11) NOT NULL,
  virus_id int(11) NOT NULL,
  created timestamp NOT NULL DEFAULT current_timestamp(),
  active tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (id),
  KEY K__IV_injection_id (injection_id),
  KEY K__IV_virus_id (virus_id),
  CONSTRAINT FK__IV_injection_id FOREIGN KEY (injection_id) REFERENCES injection (id) ON UPDATE CASCADE,
  CONSTRAINT FK__IV_virus_id FOREIGN KEY (virus_id) REFERENCES virus (id) ON UPDATE CASCADE
)

##
## Table structure for table organic_label
##
@schema
class OrganicLabel(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  label_id varchar(20) NOT NULL,
  label_type enum('Cascade Blue','Chicago Blue','Alexa405','Alexa488','Alexa647','Cy2','Cy3','Cy5','Cy5.5','Cy7','Fluorescein','Rhodamine B','Rhodamine 6G','Texas Red','TMR') DEFAULT NULL,
  type_lot_number varchar(20) DEFAULT NULL,
  type_tracer enum('BDA','Dextran','FluoroGold','DiI','DiO') DEFAULT NULL,
  type_details varchar(500) DEFAULT NULL,
  concentration float NOT NULL DEFAULT 0 COMMENT '(µM) if applicable',
  excitation_1p_wavelength int(11) NOT NULL DEFAULT 0 COMMENT '(nm)',
  excitation_1p_range int(11) NOT NULL DEFAULT 0 COMMENT '(nm)',
  excitation_2p_wavelength int(11) NOT NULL DEFAULT 0 COMMENT '(nm)',
  excitation_2p_range int(11) NOT NULL DEFAULT 0 COMMENT '(nm)',
  lp_dichroic_cut int(11) NOT NULL DEFAULT 0 COMMENT '(nm)',
  emission_wavelength int(11) NOT NULL DEFAULT 0 COMMENT '(nm)',
  emission_range int(11) NOT NULL DEFAULT 0 COMMENT '(nm)',
  label_source enum('','Invitrogen','Sigma','Thermo-Fisher') DEFAULT NULL,
  source_details varchar(100) DEFAULT NULL,
  comments varchar(2000) DEFAULT NULL COMMENT 'assessment',
  created timestamp NOT NULL DEFAULT current_timestamp(),
  active tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (id)
)

##
## Table structure for table progress_lookup
##
@schema
class ProgressLookup(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  ordinal int(11) NOT NULL,
  description varchar(200) NOT NULL,
  original_step varchar(50) DEFAULT NULL,
  category varchar(200) NOT NULL,
  script varchar(200) DEFAULT NULL,
  active tinyint(4) NOT NULL DEFAULT 1,
  created timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  UNIQUE KEY UK__lookup_ordinal (ordinal)
)

##
## Table structure for table resource
##
@schema
class Resource(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  first_name varchar(30) NOT NULL,
  last_name varchar(30) NOT NULL,
  role_id int(11) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY K__RESOURCE_role_id (role_id),
  CONSTRAINT FK__RESOURCE_role_id FOREIGN KEY (role_id) REFERENCES task_roles (id) ON DELETE CASCADE ON UPDATE CASCADE
)


##
## Table structure for table scan_run
##
@schema
class ScanRun(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  prep_id varchar(200) NOT NULL,
  performance_center enum('CSHL','Salk','UCSD','HHMI') DEFAULT NULL COMMENT 'default population is from Histology',
  machine enum('Zeiss','Axioscan','Nanozoomer','Olympus VA') DEFAULT NULL,
  objective enum('60X','40X','20X','10X') DEFAULT NULL,
  resolution float NOT NULL DEFAULT 0 COMMENT '(µm) lateral resolution if available',
  number_of_slides int(11) NOT NULL DEFAULT 0,
  scan_date date DEFAULT NULL,
  file_type enum('CZI','JPEG2000','NDPI','NGR') DEFAULT NULL,
  scenes_per_slide enum('1','2','3','4','5','6') DEFAULT NULL,
  section_schema enum('L to R','R to L') DEFAULT NULL COMMENT 'agreement is one row',
  channels_per_scene enum('1','2','3','4') DEFAULT NULL,
  slide_folder_path varchar(200) DEFAULT NULL COMMENT 'the path to the slides folder on birdstore (files to be converted)',
  converted_folder_path varchar(200) DEFAULT NULL COMMENT 'the path to the slides folder on birdstore after convertion',
  converted_status enum('not started','converted','converting','error') DEFAULT NULL,
  ch_1_filter_set enum('68','47','38','46','63','64','50') DEFAULT NULL COMMENT 'This is counterstain Channel',
  ch_2_filter_set enum('68','47','38','46','63','64','50') DEFAULT NULL,
  ch_3_filter_set enum('68','47','38','46','63','64','50') DEFAULT NULL,
  ch_4_filter_set enum('68','47','38','46','63','64','50') DEFAULT NULL,
  comments varchar(2001) DEFAULT NULL COMMENT 'assessment',
  active tinyint(4) NOT NULL DEFAULT 1,
  created timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  KEY FK__scan_run_prep_id (prep_id),
  CONSTRAINT FK__scan_run_prep_id FOREIGN KEY (prep_id) REFERENCES animal (prep_id)
)

##
## Table structure for table section
##
@schema
class Section(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  prep_id varchar(200) NOT NULL,
  file_name varchar(200) NOT NULL,
  section_number int(11) NOT NULL,
  section_qc enum('OK','Missing','Replace') NOT NULL,
  ch_1_path varchar(200) DEFAULT NULL,
  ch_2_path varchar(200) DEFAULT NULL,
  ch_3_path varchar(200) DEFAULT NULL,
  ch_4_path varchar(200) DEFAULT NULL,
  comments varchar(2001) DEFAULT NULL,
  active tinyint(4) NOT NULL DEFAULT 1,
  created timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  KEY K__section_prep_id (prep_id),
  CONSTRAINT FK__section_prep_id FOREIGN KEY (prep_id) REFERENCES animal (prep_id)
)

##
## Table structure for table slide
##
@schema
class Slide(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  scan_run_id int(11) NOT NULL,
  slide_physical_id int(11) NOT NULL COMMENT 'one per slide',
  rescan_number enum('','1','2','3') NOT NULL DEFAULT '',
  slide_status enum('Bad','Good') NOT NULL DEFAULT 'Good',
  insert_before_one tinyint(4) NOT NULL DEFAULT 0,
  scene_qc_1 enum('Out-of-Focus','Bad tissue') DEFAULT NULL,
  insert_between_one_two tinyint(4) NOT NULL DEFAULT 0,
  scene_qc_2 enum('Out-of-Focus','Bad tissue') DEFAULT NULL,
  insert_between_two_three tinyint(4) NOT NULL DEFAULT 0,
  scene_qc_3 enum('Out-of-Focus','Bad tissue') DEFAULT NULL,
  insert_between_three_four tinyint(4) NOT NULL DEFAULT 0,
  scene_qc_4 enum('Out-of-Focus','Bad tissue') DEFAULT NULL,
  insert_between_four_five tinyint(4) NOT NULL DEFAULT 0,
  scene_qc_5 enum('Out-of-Focus','Bad tissue') DEFAULT NULL,
  insert_between_five_six tinyint(4) NOT NULL DEFAULT 0,
  scene_qc_6 enum('Out-of-Focus','Bad tissue') DEFAULT NULL,
  file_name varchar(200) NOT NULL,
  comments varchar(2001) DEFAULT NULL COMMENT 'assessment',
  active tinyint(4) NOT NULL DEFAULT 1,
  created timestamp NULL DEFAULT current_timestamp(),
  file_size float NOT NULL DEFAULT 0,
  processing_duration float NOT NULL DEFAULT 0,
  processed tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  KEY K__slide_scan_run_id (scan_run_id),
  CONSTRAINT FK__slide_scan_run_id FOREIGN KEY (scan_run_id) REFERENCES scan_run (id) ON UPDATE CASCADE
) 

##
## Table structure for table slide_czi_to_tif
##
@schema
class SlideCziToTif(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  slide_id int(11) NOT NULL,
  file_name varchar(200) NOT NULL,
  section_number int(11) NOT NULL,
  scene_number tinyint(4) NOT NULL,
  channel tinyint(4) NOT NULL,
  width int(11) NOT NULL DEFAULT 0,
  height int(11) NOT NULL DEFAULT 0,
  comments varchar(2000) DEFAULT NULL COMMENT 'assessment',
  active tinyint(4) NOT NULL DEFAULT 1,
  created timestamp NULL DEFAULT current_timestamp(),
  file_size float NOT NULL DEFAULT 0,
  channel_index int(11) NOT NULL DEFAULT 0,
  scene_index int(11) NOT NULL DEFAULT 0,
  processing_duration float NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  KEY K__slide_id (slide_id),
  CONSTRAINT FK__slide_id FOREIGN KEY (slide_id) REFERENCES slide (id) ON DELETE CASCADE ON UPDATE CASCADE
) 

##
## Table structure for table task
##
@schema
class Task(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  lookup_id int(11) NOT NULL,
  prep_id varchar(20) NOT NULL,
  completed tinyint(4) NOT NULL DEFAULT 0,
  start_date datetime DEFAULT NULL,
  end_date datetime DEFAULT NULL,
  active tinyint(4) NOT NULL DEFAULT 1,
  created timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (id),
  UNIQUE KEY UK__progress_data_prep_lookup (prep_id,lookup_id),
  KEY K__progress_data_prep_id (prep_id),
  KEY K__progress_data_lookup_id (lookup_id),
  CONSTRAINT FK__progress_data_lookup_id FOREIGN KEY (lookup_id) REFERENCES progress_lookup (id),
  CONSTRAINT FK__progress_data_prep_id FOREIGN KEY (prep_id) REFERENCES animal (prep_id)
);

##
## Table structure for table task_resources
##
@schema
class TaskResources(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  task_id int(11) NOT NULL,
  resource_id int(11) NOT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY UK__TR_task_id (task_id,resource_id),
  KEY K__TR_resource_id (resource_id),
  CONSTRAINT FK__TR_resource_id FOREIGN KEY (resource_id) REFERENCES resource (id) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT FK__TR_task_id FOREIGN KEY (task_id) REFERENCES task (id) ON DELETE CASCADE ON UPDATE CASCADE
);

##
## Table structure for table task_roles
##
@schema
class Task_roles(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  name varchar(30) NOT NULL,
  PRIMARY KEY (id)
);

##
## Table structure for table virus
##
@schema
class Virus(dj.Manual):
  id int(11) NOT NULL AUTO_INCREMENT,
  virus_name varchar(50) NOT NULL,
  virus_type enum('Adenovirus','AAV','CAV','DG rabies','G-pseudo-Lenti','Herpes','Lenti','N2C rabies','Sinbis') DEFAULT NULL,
  virus_active enum('yes','no') DEFAULT NULL,
  type_details varchar(500) DEFAULT NULL,
  titer float NOT NULL DEFAULT 0 COMMENT '(particles/ml) if applicable',
  lot_number varchar(20) DEFAULT NULL,
  label enum('YFP','GFP','RFP','histo-tag') DEFAULT NULL,
  label2 varchar(200) DEFAULT NULL,
  excitation_1p_wavelength int(11) NOT NULL DEFAULT 0 COMMENT '(nm) if applicable',
  excitation_1p_range int(11) NOT NULL DEFAULT 0 COMMENT '(nm) if applicable',
  excitation_2p_wavelength int(11) NOT NULL DEFAULT 0 COMMENT '(nm) if applicable',
  excitation_2p_range int(11) NOT NULL DEFAULT 0 COMMENT '(nm) if applicable',
  lp_dichroic_cut int(11) NOT NULL DEFAULT 0 COMMENT '(nm) if applicable',
  emission_wavelength int(11) NOT NULL DEFAULT 0 COMMENT '(nm) if applicable',
  emission_range int(11) NOT NULL DEFAULT 0 COMMENT '(nm) if applicable0',
  virus_source enum('Adgene','Salk','Penn','UNC') DEFAULT NULL,
  source_details varchar(100) DEFAULT NULL,
  comments varchar(2000) DEFAULT NULL COMMENT 'assessment',
  created timestamp NOT NULL DEFAULT current_timestamp(),
  active tinyint(4) NOT NULL DEFAULT 1,
  PRIMARY KEY (id)
);
