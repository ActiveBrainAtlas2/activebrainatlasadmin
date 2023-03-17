-- MariaDB dump 10.19  Distrib 10.6.12-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: brainsharer
-- ------------------------------------------------------
-- Server version	10.6.12-MariaDB-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- make sure we are in the correct database!!!
use brainsharer;

-- here are list of all the tables that are not being used, they
-- are either deprecated, or not necessary or not being used
DROP TABLE IF EXISTS `annotations_point_archive`;
DROP TABLE IF EXISTS `annotations_points`;
DROP TABLE IF EXISTS `background_task`;
DROP TABLE IF EXISTS `background_task_completedtask`;
DROP TABLE IF EXISTS `biocyc`;
DROP TABLE IF EXISTS `biosource`;
DROP TABLE IF EXISTS `structure`;
DROP TABLE IF EXISTS `neuroglancer_urls`;

--
-- Table structure for table `animal`
--

DROP TABLE IF EXISTS `animal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `animal` (
  `prep_id` varchar(20) NOT NULL COMMENT 'Name for lab mouse/rat, max 20 chars',
  `FK_lab_id` int(11) DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL COMMENT 'the mouse''s date of birth',
  `species` enum('mouse','rat') DEFAULT NULL,
  `strain` varchar(50) DEFAULT NULL,
  `sex` enum('M','F') DEFAULT NULL COMMENT '(M/F) either ''M'' for male, ''F'' for female',
  `genotype` varchar(100) DEFAULT NULL COMMENT 'transgenic description, usually "C57"; We will need a genotype table',
  `vender` enum('Jackson','Charles River','Harlan','NIH','Taconic') DEFAULT NULL,
  `stock_number` varchar(100) DEFAULT NULL COMMENT 'if not from a performance center',
  `tissue_source` enum('animal','brain','slides') DEFAULT NULL,
  `ship_date` date DEFAULT NULL,
  `shipper` enum('FedEx','UPS') DEFAULT NULL,
  `tracking_number` varchar(100) DEFAULT NULL,
  `alias` varchar(100) DEFAULT NULL COMMENT 'names given by others',
  `comments` varchar(2001) DEFAULT NULL COMMENT 'assessment',
  `active` tinyint(1) NOT NULL DEFAULT 1,
  created datetime(6),
  `updated` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`prep_id`),
  KEY `K__animal_lab` (`FK_lab_id`),
  CONSTRAINT `FK__animal_lab` FOREIGN KEY (`FK_lab_id`) REFERENCES `auth_lab` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `annotation_session`
--

DROP TABLE IF EXISTS `annotation_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `annotation_session` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `annotation_type` enum('POLYGON_SEQUENCE','MARKED_CELL','STRUCTURE_COM') DEFAULT NULL,
  `FK_user_id` int(11) NOT NULL,
  `FK_prep_id` varchar(20) NOT NULL,
  `FK_state_id` int(11) DEFAULT NULL,
  `FK_brain_region_id` int(11) NOT NULL COMMENT 'TABLE brain_region SHOULD ONLY CONTAIN BIOLOGICAL STRUCTURES',
  `active` tinyint(1) NOT NULL DEFAULT 0,
  `created` datetime(6) NOT NULL,
  `updated` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `K__annotation_session_FK)user_id` (`FK_user_id`),
  KEY `K__annotation_session_FK_prep_id` (`FK_prep_id`),
  KEY `K__annotation_session_FK_brain_region_id` (`FK_brain_region_id`),
  KEY `K__annotation_session_annotation_type_active` (`active`,`annotation_type`),
  CONSTRAINT `FK__annotation_session_annotator` FOREIGN KEY (`FK_user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `FK__annotation_session_animal` FOREIGN KEY (`FK_prep_id`) REFERENCES `animal` (`prep_id`),
  CONSTRAINT `FK__annotation_session_brain_region` FOREIGN KEY (`FK_brain_region_id`) REFERENCES `brain_region` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;



--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__auth_group_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__auth_group_permissions_group_id_permission_id` (`group_id`,`permission_id`),
  KEY `K__auth_group_permissions_permission_id` (`permission_id`),
  CONSTRAINT `FK__auth_group_permissions_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `FK__auth_group_permissions_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_lab`
--

DROP TABLE IF EXISTS `auth_lab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_lab` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `lab_name` varchar(100) NOT NULL,
  `lab_url` varchar(250) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__auth_permission_content_type_id_codename` (`content_type_id`,`codename`),
  CONSTRAINT `FK__auth_permission_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(150) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  `FK_lab_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__auth_user_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__authentication_user_groups_user_id_group_id` (`user_id`,`group_id`),
  KEY `K__authentication_user_groups_group_id` (`group_id`),
  CONSTRAINT `FK__authentication_user__user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `FK__authentication_user_groups_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `auth_user_labs`
--

DROP TABLE IF EXISTS `auth_user_labs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_labs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `lab_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__auth_user_labs_user_id_lab_id` (`user_id`,`lab_id`),
  KEY `K__auth_user_labs_lab_id` (`lab_id`),
  CONSTRAINT `FK__auth_user_labs_lab_id` FOREIGN KEY (`lab_id`) REFERENCES `auth_lab` (`id`),
  CONSTRAINT `FK__auth_user_labs_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__auth_user_user_permissions_user_id_permission_id` (`user_id`,`permission_id`),
  KEY `K__auth_user__permission_id` (`permission_id`),
  CONSTRAINT `FK__auth_user_user_permission_permission_id` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `FK__auth_user_user_permission_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `available_neuroglancer_data`
--

DROP TABLE IF EXISTS `available_neuroglancer_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `available_neuroglancer_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_name` varchar(50) NOT NULL,
  `FK_lab_id` int(11) NOT NULL,
  `layer_name` varchar(255) NOT NULL,
  `description` varchar(2001) DEFAULT NULL,
  `url` varchar(2001) DEFAULT NULL,
  `thumbnail_url` varchar(2001) DEFAULT NULL,
  `layer_type` varchar(25) NOT NULL,
  `cross_section_orientation` varchar(255) DEFAULT NULL,
  `resolution` float NOT NULL DEFAULT 0,
  `zresolution` float NOT NULL DEFAULT 0,
  `width` int(11) NOT NULL DEFAULT 60000,
  `height` int(11) NOT NULL DEFAULT 30000,
  `depth` int(11) NOT NULL DEFAULT 450,
  `max_range` int(11) NOT NULL DEFAULT 5000,
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `created` datetime NOT NULL,
  `updated` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `K__available_nd_lab_id` (`FK_lab_id`),
  KEY `K__AND_group_name` (`group_name`),
  CONSTRAINT `FK__available_nd_lab_id` FOREIGN KEY (`FK_lab_id`) REFERENCES `auth_lab` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `brain_atlas`
--

DROP TABLE IF EXISTS `brain_atlas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `brain_atlas` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `atlas_name` varchar(64) NOT NULL,
  `description` longtext DEFAULT NULL,
  `FK_lab_id` int(11) NOT NULL,
  `resolution` double NOT NULL,
  `url` longtext NOT NULL,
  `zresolution` double NOT NULL,
  PRIMARY KEY (`id`),
  KEY `K__brain_atlas_FK_lab_id` (`FK_lab_id`),
  CONSTRAINT `FK__brain_atlas_auth_lab` FOREIGN KEY (`FK_lab_id`) REFERENCES `auth_lab` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `brain_region`
-- this table replaces structure

DROP TABLE IF EXISTS `brain_region`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `brain_region` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `abbreviation` varchar(200) NOT NULL,
  `description` longtext DEFAULT NULL,
  `FK_ref_atlas_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `K__brain_region_FK_ref_atlas_id` (`FK_ref_atlas_id`),
  CONSTRAINT `FK__brain_region_brain_atlas` FOREIGN KEY (`FK_ref_atlas_id`) REFERENCES `brain_atlas` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `cell_type`
--

DROP TABLE IF EXISTS `cell_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cell_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cell_type` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `created` datetime(6) NOT NULL DEFAULT current_timestamp(6),
  PRIMARY KEY (`id`),
  KEY `K__CT_INID` (`cell_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext DEFAULT NULL,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL CHECK (`action_flag` >= 0),
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `K_django_admin_log_content_type_id` (`content_type_id`),
  KEY `K_django_admin_log_user_id` (`user_id`),
  CONSTRAINT `FK__django_admin_log_content_type_id` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `FK__django_admin_log_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__django_content_type_app_label_model` (`app_label`,`model`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_plotly_dash_dashapp`
--

DROP TABLE IF EXISTS `django_plotly_dash_dashapp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_plotly_dash_dashapp` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `instance_name` varchar(100) NOT NULL,
  `slug` varchar(110) NOT NULL,
  `base_state` longtext NOT NULL,
  `creation` datetime(6) NOT NULL,
  `update` datetime(6) NOT NULL,
  `save_on_change` tinyint(1) NOT NULL,
  `stateless_app_id` bigint(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__dpdd_instance_name` (`instance_name`),
  UNIQUE KEY `UK__dpdd_slug` (`slug`),
  KEY `K__dpdd_stateless_app_id` (`stateless_app_id`),
  CONSTRAINT `FK__dpdd_stateless_app_id` FOREIGN KEY (`stateless_app_id`) REFERENCES `django_plotly_dash_statelessapp` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `django_plotly_dash_statelessapp`
--

DROP TABLE IF EXISTS `django_plotly_dash_statelessapp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_plotly_dash_statelessapp` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `app_name` varchar(100) NOT NULL,
  `slug` varchar(110) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__dpds_app_name` (`app_name`),
  UNIQUE KEY `UK__dpds_slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `K__django_session_expire_date` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__django_site_domain` (`domain`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `histology`
--

DROP TABLE IF EXISTS `histology`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `histology` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prep_id` varchar(20) NOT NULL,
  `virus_id` int(11) DEFAULT NULL,
  `performance_center` enum('CSHL','Salk','UCSD','HHMI') DEFAULT NULL COMMENT 'default population is from Injection',
  `anesthesia` enum('ketamine','isoflurane','pentobarbital','fatal plus') DEFAULT NULL,
  `perfusion_age_in_days` tinyint(3) unsigned NOT NULL DEFAULT 0,
  `perfusion_date` date DEFAULT NULL,
  `exsangination_method` enum('PBS','aCSF','Ringers') DEFAULT NULL,
  `fixative_method` enum('Para','Glut','Post fix') DEFAULT NULL,
  `special_perfusion_notes` varchar(200) DEFAULT NULL,
  `post_fixation_period` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT '(days)',
  `whole_brain` enum('Y','N') DEFAULT NULL,
  `block` varchar(200) DEFAULT NULL COMMENT 'if applicable',
  `date_sectioned` date DEFAULT NULL,
  `side_sectioned_first` enum('ASC','DESC') NOT NULL DEFAULT 'ASC',
  `sectioning_method` enum('cryoJane','cryostat','vibratome','optical','sliding microtiome') DEFAULT NULL,
  `section_thickness` tinyint(3) unsigned NOT NULL DEFAULT 20 COMMENT '(µm)',
  `orientation` enum('coronal','horizontal','sagittal','oblique') DEFAULT NULL,
  `oblique_notes` varchar(200) DEFAULT NULL,
  `mounting` enum('every section','2nd','3rd','4th','5ft','6th') DEFAULT NULL COMMENT 'used to automatically populate Placeholder',
  `counterstain` enum('thionin','NtB','NtFR','DAPI','Giemsa','Syto41') DEFAULT NULL,
  `comments` varchar(2001) DEFAULT NULL COMMENT 'assessment',
  `created` timestamp NOT NULL DEFAULT current_timestamp(),
  `active` tinyint(4) NOT NULL DEFAULT 1,
  `scene_order` enum('ASC','DESC') DEFAULT 'ASC',
  PRIMARY KEY (`id`),
  KEY `K__histology_virus_id` (`virus_id`),
  KEY `K__histology_prep_id` (`prep_id`),
  CONSTRAINT `FK__histology_prep_id` FOREIGN KEY (`prep_id`) REFERENCES `animal` (`prep_id`) ON UPDATE CASCADE,
  CONSTRAINT `FK__histology_virus_id` FOREIGN KEY (`virus_id`) REFERENCES `virus` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;


--
-- Table structure for table `injection`
--

DROP TABLE IF EXISTS `injection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `injection` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `anesthesia` enum('ketamine','isoflurane') DEFAULT NULL,
  `method` enum('iontophoresis','pressure','volume') DEFAULT NULL,
  `pipet` enum('glass','quartz','Hamilton','syringe needle') DEFAULT NULL,
  `location` varchar(20) DEFAULT NULL,
  `angle` varchar(20) DEFAULT NULL,
  `brain_location_dv` double NOT NULL,
  `brain_location_ml` double NOT NULL,
  `brain_location_ap` double NOT NULL,
  `injection_date` date DEFAULT NULL,
  `transport_days` int(11) NOT NULL,
  `virus_count` int(11) NOT NULL,
  `comments` longtext DEFAULT NULL,
  `injection_volume` varchar(20) DEFAULT NULL,
  `FK_prep_id` varchar(20) NOT NULL,
  `FK_lab_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `K__injection_FK_prep_id` (`FK_prep_id`),
  KEY `K__injection_FK_lab_id` (`FK_lab_id`),
  CONSTRAINT `FK__injection_animal` FOREIGN KEY (`FK_prep_id`) REFERENCES `animal` (`prep_id`),
  CONSTRAINT `FK__injection_lab` FOREIGN KEY (`FK_lab_id`) REFERENCES `auth_lab` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
--
-- Table structure for table `injection_virus`
--

DROP TABLE IF EXISTS `injection_virus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `injection_virus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `FK_injection_id` int(11) NOT NULL,
  `FK_virus_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `K__injection_virus_FK_injection_id` (`FK_injection_id`),
  KEY `K__injection_virus_FK_virus_id` (`FK_virus_id`),
  CONSTRAINT `FK__injection_virus_FK_injection_id` FOREIGN KEY (`FK_injection_id`) REFERENCES `injection` (`id`),
  CONSTRAINT `FK__injection_virus_FK_virus_id` FOREIGN KEY (`FK_virus_id`) REFERENCES `virus` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `marked_cells`
--

DROP TABLE IF EXISTS `marked_cells`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `marked_cells` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source` enum('MACHINE_SURE','MACHINE_UNSURE','HUMAN_POSITIVE','HUMAN_NEGATIVE','UNMARKED') NOT NULL,
  `x` decimal(8,2) NOT NULL DEFAULT 0.00,
  `y` decimal(8,2) NOT NULL DEFAULT 0.00,
  `z` decimal(8,2) NOT NULL DEFAULT 0.00,
  `FK_session_id` int(11) NOT NULL COMMENT 'annotation session that the cell belong to',
  `FK_cell_type_id` int(11) DEFAULT NULL COMMENT 'cell type of the cell ',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__marked_cells_session_xyz` (`FK_session_id`,`x`,`y`,`z`),
  KEY `K__marked_cells_session_id` (`FK_session_id`),
  KEY `K__marked_cells_cell_type_id` (`FK_cell_type_id`),
  CONSTRAINT `FK__marked_cells_annotation_session` FOREIGN KEY (`FK_session_id`) REFERENCES `annotation_session` (`id`),
  CONSTRAINT `FK__marked_cells_cell_type` FOREIGN KEY (`FK_cell_type_id`) REFERENCES `cell_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mouselight_neuron`
--

DROP TABLE IF EXISTS `mouselight_neuron`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `mouselight_neuron` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `idstring` varchar(64) NOT NULL,
  `sample_date` datetime(6) DEFAULT NULL,
  `sample_strain` varchar(255) DEFAULT NULL,
  `virus_label` varchar(255) DEFAULT NULL,
  `fluorophore_label` varchar(255) DEFAULT NULL,
  `annotation_space` varchar(20) NOT NULL,
  `soma_atlas_id` int(10) unsigned DEFAULT NULL CHECK (`soma_atlas_id` >= 0),
  `axon_endpoints_dict` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`axon_endpoints_dict`)),
  `axon_branches_dict` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`axon_branches_dict`)),
  `dendrite_endpoints_dict` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`dendrite_endpoints_dict`)),
  `dendrite_branches_dict` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`dendrite_branches_dict`)),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `neuroglancer_state`
--

DROP TABLE IF EXISTS `neuroglancer_state`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `neuroglancer_state` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `neuroglancer_state` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL CHECK (json_valid(`neuroglancer_state`)),
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `user_date` varchar(25),
  `comments` varchar(255) NOT NULL,
  `FK_user_id` int(11) DEFAULT NULL,
  `readonly` tinyint(1) NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `K__neuroglancer_state_FK_user_id` (`FK_user_id`),
  CONSTRAINT `FK__neuroglancer_state_auth_user` FOREIGN KEY (`FK_user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Table structure for table `polygon_sequences`
--

DROP TABLE IF EXISTS `polygon_sequences`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `polygon_sequences` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source` enum('NA') DEFAULT NULL COMMENT 'PLACEHOLDER FIELD',
  `x` decimal(8,2) NOT NULL DEFAULT 0.00,
  `y` decimal(8,2) NOT NULL DEFAULT 0.00,
  `z` decimal(8,2) NOT NULL DEFAULT 0.00,
  `polygon_index` int(11) DEFAULT NULL COMMENT 'ORDERING (INDEX) OF POLYGONS ACROSS VOLUMES',
  `point_order` int(11) NOT NULL DEFAULT 0,
  `FK_session_id` int(11) NOT NULL COMMENT 'CREATOR/EDITOR',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_ps_session_xyz_index` (`FK_session_id`,`x`,`y`,`z`,`polygon_index`,`point_order`),
  KEY `FK_session_id` (`FK_session_id`),
  CONSTRAINT `FK_polygon_sequences_annotation_session` FOREIGN KEY (`FK_session_id`) REFERENCES `annotation_session` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `slide`
--

DROP TABLE IF EXISTS `slide`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `slide` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `FK_scan_run_id` int(11) NOT NULL,
  `slide_physical_id` int(11) NOT NULL COMMENT 'one per slide',
  `slide_status` enum('Bad','Good') NOT NULL DEFAULT 'Good',
  `scenes` int(11) DEFAULT NULL,
  `insert_before_one` tinyint(4) NOT NULL DEFAULT 0,
  `insert_between_one_two` tinyint(4) NOT NULL DEFAULT 0,
  `insert_between_two_three` tinyint(4) NOT NULL DEFAULT 0,
  `insert_between_three_four` tinyint(4) NOT NULL DEFAULT 0,
  `insert_between_four_five` tinyint(4) NOT NULL DEFAULT 0,
  `insert_between_five_six` tinyint(4) NOT NULL DEFAULT 0,
  `file_name` varchar(200) NOT NULL,
  `comments` varchar(2001) DEFAULT NULL COMMENT 'assessment',
  `active` tinyint(4) NOT NULL DEFAULT 1,
  `created` timestamp NULL DEFAULT current_timestamp(),
  `file_size` float NOT NULL DEFAULT 0,
  `processing_duration` float NOT NULL DEFAULT 0,
  `processed` tinyint(4) NOT NULL DEFAULT 0,
  `scene_qc_1` tinyint(4) NOT NULL DEFAULT 0,
  `scene_qc_2` tinyint(4) NOT NULL DEFAULT 0,
  `scene_qc_3` tinyint(4) NOT NULL DEFAULT 0,
  `scene_qc_4` tinyint(4) NOT NULL DEFAULT 0,
  `scene_qc_5` tinyint(4) NOT NULL DEFAULT 0,
  `scene_qc_6` tinyint(4) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `K__slide_scan_run` (`FK_scan_run_id`),
  CONSTRAINT `FK__slide_scan_run` FOREIGN KEY (`FK_scan_run_id`) REFERENCES `scan_run` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB  DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `slide_czi_to_tif`
--

DROP TABLE IF EXISTS `slide_czi_to_tif`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `slide_czi_to_tif` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `FK_slide_id` int(11) NOT NULL,
  `file_name` varchar(200) NOT NULL,
  `scene_number` tinyint(4) NOT NULL,
  `channel` tinyint(4) NOT NULL,
  `width` int(11) NOT NULL DEFAULT 0,
  `height` int(11) NOT NULL DEFAULT 0,
  `comments` varchar(2000) DEFAULT NULL COMMENT 'assessment',
  `active` tinyint(4) NOT NULL DEFAULT 1,
  `created` timestamp NULL DEFAULT current_timestamp(),
  `file_size` float NOT NULL DEFAULT 0,
  `scene_index` int(11) NOT NULL DEFAULT 0,
  `processing_duration` float NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `K__slide_id` (`FK_slide_id`),
  CONSTRAINT `FK__slide_id` FOREIGN KEY (`FK_slide_id`) REFERENCES `slide` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Table structure for table `scan_run`
--

DROP TABLE IF EXISTS `scan_run`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scan_run` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `FK_prep_id` varchar(20) NOT NULL,
  `rescan_number` tinyint(4) NOT NULL DEFAULT 0,
  `performance_center` enum('CSHL','Salk','UCSD','HHMI') DEFAULT NULL COMMENT 'default population is from Histology',
  `machine` enum('Axioscan I','Axioscan II') DEFAULT NULL,
  `objective` enum('60X','40X','20X','10X') DEFAULT NULL,
  `resolution` float NOT NULL DEFAULT 0 COMMENT '(µm) lateral resolution if available',
  `zresolution` float NOT NULL DEFAULT 20,
  `number_of_slides` int(11) NOT NULL DEFAULT 0,
  `scan_date` date DEFAULT NULL,
  `file_type` enum('CZI','JPEG2000','NDPI','NGR') DEFAULT NULL,
  `scenes_per_slide` enum('1','2','3','4','5','6') DEFAULT NULL,
  `section_schema` enum('L to R','R to L') DEFAULT NULL COMMENT 'agreement is one row',
  `channels_per_scene` enum('1','2','3','4') DEFAULT NULL,
  `slide_folder_path` varchar(200) DEFAULT NULL COMMENT 'the path to the slides folder on birdstore (files to be converted)',
  `converted_status` enum('not started','converted','converting','error') DEFAULT NULL,
  `ch_1_filter_set` enum('68','47','38','46','63','64','50') DEFAULT NULL COMMENT 'This is counterstain Channel',
  `ch_2_filter_set` enum('68','47','38','46','63','64','50') DEFAULT NULL,
  `ch_3_filter_set` enum('68','47','38','46','63','64','50') DEFAULT NULL,
  `ch_4_filter_set` enum('68','47','38','46','63','64','50') DEFAULT NULL,
  `width` int(11) NOT NULL DEFAULT 0,
  `height` int(11) NOT NULL DEFAULT 0,
  `rotation` int(11) NOT NULL DEFAULT 0,
  `flip` enum('none','flip','flop') NOT NULL DEFAULT 'none',
  `comments` varchar(2001) DEFAULT NULL COMMENT 'assessment',
  `active` tinyint(4) NOT NULL DEFAULT 1,
  `created` datetime(6) NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `FK__scan_run_FK_prep_id` (`FK_prep_id`),
  CONSTRAINT `FK__scan_run_FK_prep_id` FOREIGN KEY (`FK_prep_id`) REFERENCES `animal` (`prep_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


--
-- Table structure for table `structure_com`
--

DROP TABLE IF EXISTS `structure_com`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `structure_com` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `source` enum('MANUAL','COMPUTER') DEFAULT NULL,
  `x` decimal(8,2) NOT NULL DEFAULT 0.00,
  `y` decimal(8,2) NOT NULL DEFAULT 0.00,
  `z` decimal(8,2) NOT NULL DEFAULT 0.00,
  `FK_session_id` int(11) NOT NULL COMMENT 'CREATOR/EDITOR',
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_sc_session_xyz` (`source`,`x`,`y`,`z`,`FK_session_id`),
  KEY `FK_session_id` (`FK_session_id`),
  CONSTRAINT `FK__structure_com_annotation_session` FOREIGN KEY (`FK_session_id`) REFERENCES `annotation_session` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
--
-- Table structure for table `viral_tracing_layer`
--

DROP TABLE IF EXISTS `viral_tracing_layer`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `viral_tracing_layer` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `brain_name` varchar(128) NOT NULL,
  `virus` varchar(32) NOT NULL,
  `timepoint` varchar(32) NOT NULL,
  `primary_inj_site` varchar(32) DEFAULT NULL,
  `frac_inj_lob_i_v` double DEFAULT NULL,
  `frac_inj_lob_vi_vii` double DEFAULT NULL,
  `frac_inj_lob_viii_x` double DEFAULT NULL,
  `frac_inj_simplex` double DEFAULT NULL,
  `frac_inj_crusi` double DEFAULT NULL,
  `frac_inj_crusii` double DEFAULT NULL,
  `frac_inj_pm_cp` double DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `virus`
--

DROP TABLE IF EXISTS `virus`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `virus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `virus_name` varchar(50) NOT NULL,
  `virus_type` enum('Adenovirus','AAV','CAV','DG rabies','G-pseudo-Lenti','Herpes','Lenti','N2C rabies','Sinbis') DEFAULT NULL,
  `virus_active` enum('yes','no') DEFAULT NULL,
  `type_details` varchar(500) DEFAULT NULL,
  `titer` double NOT NULL,
  `lot_number` varchar(20) DEFAULT NULL,
  `label` enum('YFP','GFP','RFP','histo-tag') DEFAULT NULL,
  `excitation_1p_wavelength` int(11) NOT NULL,
  `excitation_1p_range` int(11) NOT NULL,
  `excitation_2p_wavelength` int(11) NOT NULL,
  `excitation_2p_range` int(11) NOT NULL,
  `lp_dichroic_cut` int(11) NOT NULL,
  `emission_wavelength` int(11) NOT NULL,
  `emission_range` int(11) NOT NULL,
  `virus_source` enum('Adgene','Salk','Penn','UNC') DEFAULT NULL,
  `source_details` varchar(100) DEFAULT NULL,
  `comments` longtext DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;


DROP VIEW IF EXISTS sections;

CREATE VIEW `sections` AS
SELECT
	`sc`.`id` AS `id`,
	`a`.`prep_id` AS `prep_id`,
	`sr`.`rescan_number` AS `rescan_number`,
	`s`.`file_name` AS `czi_file`,
	`s`.`slide_physical_id` AS `slide_physical_id`,
	`s`.`id` AS `FK_slide_id`,
	`sc`.`file_name` AS `file_name`,
	`sc`.`id` AS `tif_id`,
	`sc`.`scene_number` AS `scene_number`,
	`sc`.`scene_index` AS `scene_index`,
	`sc`.`channel` AS `channel`,
	`sc`.`channel` - 1 AS `channel_index`,
	`sc`.`active` AS `active`,
	`sc`.`created` AS `created`
FROM
	(((`animal` `a`
JOIN `scan_run` `sr` ON
	(`a`.`prep_id` = `sr`.`FK_prep_id`))
JOIN `slide` `s` ON
	(`sr`.`id` = `s`.`FK_scan_run_id`))
JOIN `slide_czi_to_tif` `sc` ON
	(`s`.`id` = `sc`.`FK_slide_id`))
WHERE
	`s`.`slide_status` = 'Good'
	AND `sc`.`active` = 1;



/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-10 12:24:35
