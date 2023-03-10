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

--
-- Table structure for table `animal`
--

DROP TABLE IF EXISTS `animal`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `animal` (
  `prep_id` varchar(20) NOT NULL COMMENT 'Name for lab mouse/rat, max 20 chars',
  `performance_center` enum('CSHL','Salk','UCSD','HHMI','Duke') DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL COMMENT 'the mouse''s date of birth',
  `species` enum('mouse','rat') DEFAULT NULL,
  `strain` varchar(50) DEFAULT NULL,
  `sex` enum('M','F') DEFAULT NULL COMMENT '(M/F) either ''M'' for male, ''F'' for female',
  `genotype` varchar(100) DEFAULT NULL COMMENT 'transgenic description, usually "C57"; We will need a genotype table',
  `breeder_line` varchar(100) DEFAULT NULL COMMENT 'We will need a local breeding table',
  `vender` enum('Jackson','Charles River','Harlan','NIH','Taconic') DEFAULT NULL,
  `stock_number` varchar(100) DEFAULT NULL COMMENT 'if not from a performance center',
  `tissue_source` enum('animal','brain','slides') DEFAULT NULL,
  `ship_date` date DEFAULT NULL,
  `shipper` enum('FedEx','UPS') DEFAULT NULL,
  `tracking_number` varchar(100) DEFAULT NULL,
  `aliases_1` varchar(100) DEFAULT NULL COMMENT 'names given by others',
  `aliases_2` varchar(100) DEFAULT NULL,
  `aliases_3` varchar(100) DEFAULT NULL,
  `aliases_4` varchar(100) DEFAULT NULL,
  `aliases_5` varchar(100) DEFAULT NULL,
  `comments` varchar(2001) DEFAULT NULL COMMENT 'assessment',
  `active` tinyint(4) NOT NULL DEFAULT 1,
  `created` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`prep_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `animal`
--

LOCK TABLES `animal` WRITE;
/*!40000 ALTER TABLE `animal` DISABLE KEYS */;
/*!40000 ALTER TABLE `animal` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `annotation_session`
--

DROP TABLE IF EXISTS `annotation_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `annotation_session` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `created` datetime(6) NOT NULL,
  `updated` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `annotation_type` enum('POLYGON_SEQUENCE','MARKED_CELL','STRUCTURE_COM') DEFAULT NULL,
  `FK_annotator_id` int(11) NOT NULL,
  `FK_prep_id` varchar(20) NOT NULL,
  `FK_state_id` int(11) DEFAULT NULL,
  `FK_structure_id` int(11) NOT NULL COMMENT 'TABLE structure SHOULD ONLY CONTAIN BIOLOGICAL STRUCTURES',
  `active` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `FK_annotator_id` (`FK_annotator_id`),
  KEY `FK_prep_id` (`FK_prep_id`),
  KEY `FK_structure_id` (`FK_structure_id`),
  KEY `K__annotation_type_active` (`active`,`annotation_type`),
  CONSTRAINT `annotation_session_ibfk_1` FOREIGN KEY (`FK_annotator_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `annotation_session_ibfk_2` FOREIGN KEY (`FK_prep_id`) REFERENCES `animal` (`prep_id`),
  CONSTRAINT `annotation_session_ibfk_3` FOREIGN KEY (`FK_structure_id`) REFERENCES `structure` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9052 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `annotation_session`
--

LOCK TABLES `annotation_session` WRITE;
/*!40000 ALTER TABLE `annotation_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `annotation_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `annotations_point_archive`
--

DROP TABLE IF EXISTS `annotations_point_archive`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `annotations_point_archive` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `x` decimal(8,2) NOT NULL DEFAULT 0.00,
  `y` decimal(8,2) NOT NULL DEFAULT 0.00,
  `z` decimal(8,2) NOT NULL DEFAULT 0.00,
  `FK_archive_set_id` int(11) DEFAULT NULL,
  `polygon_id` char(40) DEFAULT NULL,
  `volume_id` char(40) DEFAULT NULL,
  `ordering` int(11) NOT NULL DEFAULT 0,
  `FK_session_id` int(11) NOT NULL,
  `polygon_index` int(11) DEFAULT NULL,
  `point_order` int(11) DEFAULT NULL,
  `source` varchar(20) DEFAULT NULL,
  `FK_cell_type_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK_session_xyz` (`FK_session_id`,`x`,`y`,`z`),
  KEY `cell_type_id` (`FK_cell_type_id`),
  CONSTRAINT `annotations_point_ibfk_1` FOREIGN KEY (`FK_cell_type_id`) REFERENCES `cell_type` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `annotations_point_archive`
--

LOCK TABLES `annotations_point_archive` WRITE;
/*!40000 ALTER TABLE `annotations_point_archive` DISABLE KEYS */;
/*!40000 ALTER TABLE `annotations_point_archive` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `annotations_points`
--

DROP TABLE IF EXISTS `annotations_points`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `annotations_points` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `label` varchar(255) NOT NULL,
  `x` double NOT NULL,
  `y` double NOT NULL,
  `z` double NOT NULL,
  `FK_animal_id` int(11) DEFAULT NULL,
  `FK_structure_id` int(11) DEFAULT NULL,
  `FK_owner_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `annotations_points_FK_animal_id_40c5eea5_fk_biosource_id` (`FK_animal_id`),
  KEY `annotations_points_FK_structure_id_4519e64d_fk_brain_region_id` (`FK_structure_id`),
  KEY `annotations_points_FK_owner_id_e8e2760b_fk_authentic` (`FK_owner_id`),
  CONSTRAINT `annotations_points_FK_animal_id_40c5eea5_fk_biosource_id` FOREIGN KEY (`FK_animal_id`) REFERENCES `biosource` (`id`),
  CONSTRAINT `annotations_points_FK_owner_id_e8e2760b_fk_authentic` FOREIGN KEY (`FK_owner_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `annotations_points_FK_structure_id_4519e64d_fk_brain_region_id` FOREIGN KEY (`FK_structure_id`) REFERENCES `brain_region` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `annotations_points`
--

LOCK TABLES `annotations_points` WRITE;
/*!40000 ALTER TABLE `annotations_points` DISABLE KEYS */;
/*!40000 ALTER TABLE `annotations_points` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_lab`
--

LOCK TABLES `auth_lab` WRITE;
/*!40000 ALTER TABLE `auth_lab` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_lab` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1861 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

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
  `FK_performance_lab` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `authentication_user_groups_user_id_group_id_8af031ac_uniq` (`user_id`,`group_id`),
  KEY `authentication_user_groups_group_id_6b5c44b7_fk_auth_group_id` (`group_id`),
  CONSTRAINT `authentication_user__user_id_30868577_fk_authentic` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `authentication_user_groups_group_id_6b5c44b7_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `authentication_user_labs_user_id_lab_id_85e83707_uniq` (`user_id`,`lab_id`),
  KEY `authentication_user__lab_id_b7c82161_fk_authentic` (`lab_id`),
  CONSTRAINT `authentication_user__lab_id_b7c82161_fk_authentic` FOREIGN KEY (`lab_id`) REFERENCES `auth_lab` (`id`),
  CONSTRAINT `authentication_user__user_id_459c7a11_fk_authentic` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_labs`
--

LOCK TABLES `auth_user_labs` WRITE;
/*!40000 ALTER TABLE `auth_user_labs` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_labs` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `authentication_user_user_user_id_permission_id_ec51b09f_uniq` (`user_id`,`permission_id`),
  KEY `authentication_user__permission_id_ea6be19a_fk_auth_perm` (`permission_id`),
  CONSTRAINT `authentication_user__permission_id_ea6be19a_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `authentication_user__user_id_736ebf7e_fk_authentic` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=457 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

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
  `active` tinyint(4) NOT NULL DEFAULT 1,
  `created` datetime NOT NULL,
  `updated` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `K__available_nd_lab_id` (`FK_lab_id`),
  KEY `K__AND_group_name` (`group_name`),
  CONSTRAINT `FK__available_nd_lab_id` FOREIGN KEY (`FK_lab_id`) REFERENCES `auth_lab` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=798 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `available_neuroglancer_data`
--

LOCK TABLES `available_neuroglancer_data` WRITE;
/*!40000 ALTER TABLE `available_neuroglancer_data` DISABLE KEYS */;
/*!40000 ALTER TABLE `available_neuroglancer_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `background_task`
--

DROP TABLE IF EXISTS `background_task`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `background_task` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `task_name` varchar(190) NOT NULL,
  `task_params` longtext NOT NULL,
  `task_hash` varchar(40) NOT NULL,
  `verbose_name` varchar(255) DEFAULT NULL,
  `priority` int(11) NOT NULL,
  `run_at` datetime(6) NOT NULL,
  `repeat` bigint(20) NOT NULL,
  `repeat_until` datetime(6) DEFAULT NULL,
  `queue` varchar(190) DEFAULT NULL,
  `attempts` int(11) NOT NULL,
  `failed_at` datetime(6) DEFAULT NULL,
  `last_error` longtext NOT NULL,
  `locked_by` varchar(64) DEFAULT NULL,
  `locked_at` datetime(6) DEFAULT NULL,
  `creator_object_id` int(10) unsigned DEFAULT NULL CHECK (`creator_object_id` >= 0),
  `creator_content_type_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `background_task_creator_content_type_61cc9af3_fk_django_co` (`creator_content_type_id`),
  KEY `background_task_task_name_4562d56a` (`task_name`),
  KEY `background_task_task_hash_d8f233bd` (`task_hash`),
  KEY `background_task_priority_88bdbce9` (`priority`),
  KEY `background_task_run_at_7baca3aa` (`run_at`),
  KEY `background_task_queue_1d5f3a40` (`queue`),
  KEY `background_task_attempts_a9ade23d` (`attempts`),
  KEY `background_task_failed_at_b81bba14` (`failed_at`),
  KEY `background_task_locked_by_db7779e3` (`locked_by`),
  KEY `background_task_locked_at_0fb0f225` (`locked_at`),
  CONSTRAINT `background_task_creator_content_type_61cc9af3_fk_django_co` FOREIGN KEY (`creator_content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `background_task`
--

LOCK TABLES `background_task` WRITE;
/*!40000 ALTER TABLE `background_task` DISABLE KEYS */;
/*!40000 ALTER TABLE `background_task` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `background_task_completedtask`
--

DROP TABLE IF EXISTS `background_task_completedtask`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `background_task_completedtask` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `task_name` varchar(190) NOT NULL,
  `task_params` longtext NOT NULL,
  `task_hash` varchar(40) NOT NULL,
  `verbose_name` varchar(255) DEFAULT NULL,
  `priority` int(11) NOT NULL,
  `run_at` datetime(6) NOT NULL,
  `repeat` bigint(20) NOT NULL,
  `repeat_until` datetime(6) DEFAULT NULL,
  `queue` varchar(190) DEFAULT NULL,
  `attempts` int(11) NOT NULL,
  `failed_at` datetime(6) DEFAULT NULL,
  `last_error` longtext NOT NULL,
  `locked_by` varchar(64) DEFAULT NULL,
  `locked_at` datetime(6) DEFAULT NULL,
  `creator_object_id` int(10) unsigned DEFAULT NULL CHECK (`creator_object_id` >= 0),
  `creator_content_type_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `background_task_comp_creator_content_type_21d6a741_fk_django_co` (`creator_content_type_id`),
  KEY `background_task_completedtask_task_name_388dabc2` (`task_name`),
  KEY `background_task_completedtask_task_hash_91187576` (`task_hash`),
  KEY `background_task_completedtask_priority_9080692e` (`priority`),
  KEY `background_task_completedtask_run_at_77c80f34` (`run_at`),
  KEY `background_task_completedtask_queue_61fb0415` (`queue`),
  KEY `background_task_completedtask_attempts_772a6783` (`attempts`),
  KEY `background_task_completedtask_failed_at_3de56618` (`failed_at`),
  KEY `background_task_completedtask_locked_by_edc8a213` (`locked_by`),
  KEY `background_task_completedtask_locked_at_29c62708` (`locked_at`),
  CONSTRAINT `background_task_comp_creator_content_type_21d6a741_fk_django_co` FOREIGN KEY (`creator_content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `background_task_completedtask`
--

LOCK TABLES `background_task_completedtask` WRITE;
/*!40000 ALTER TABLE `background_task_completedtask` DISABLE KEYS */;
/*!40000 ALTER TABLE `background_task_completedtask` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `biocyc`
--

DROP TABLE IF EXISTS `biocyc`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biocyc` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `bio_name` varchar(20) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `biocyc`
--

LOCK TABLES `biocyc` WRITE;
/*!40000 ALTER TABLE `biocyc` DISABLE KEYS */;
/*!40000 ALTER TABLE `biocyc` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `biosource`
--

DROP TABLE IF EXISTS `biosource`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `biosource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `active` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `animal_name` varchar(20) NOT NULL,
  `comments` longtext DEFAULT NULL,
  `FK_ORGID` int(11) NOT NULL,
  `lab_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `biosource_FK_ORGID_5f3fffd4_fk_biocyc_id` (`FK_ORGID`),
  KEY `biosource_lab_id_17119720_fk_authentication_lab_id` (`lab_id`),
  CONSTRAINT `biosource_FK_ORGID_5f3fffd4_fk_biocyc_id` FOREIGN KEY (`FK_ORGID`) REFERENCES `biocyc` (`id`),
  CONSTRAINT `biosource_lab_id_17119720_fk_authentication_lab_id` FOREIGN KEY (`lab_id`) REFERENCES `auth_lab` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `biosource`
--

LOCK TABLES `biosource` WRITE;
/*!40000 ALTER TABLE `biosource` DISABLE KEYS */;
/*!40000 ALTER TABLE `biosource` ENABLE KEYS */;
UNLOCK TABLES;

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
  KEY `brain_atlas_FK_lab_id_54e84092_fk_auth_lab_id` (`FK_lab_id`),
  CONSTRAINT `brain_atlas_FK_lab_id_54e84092_fk_auth_lab_id` FOREIGN KEY (`FK_lab_id`) REFERENCES `auth_lab` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brain_atlas`
--

LOCK TABLES `brain_atlas` WRITE;
/*!40000 ALTER TABLE `brain_atlas` DISABLE KEYS */;
/*!40000 ALTER TABLE `brain_atlas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `brain_region`
--

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
  KEY `brain_region_FK_ref_atlas_id_6bb86dd9_fk_brain_atlas_id` (`FK_ref_atlas_id`),
  CONSTRAINT `brain_region_FK_ref_atlas_id_6bb86dd9_fk_brain_atlas_id` FOREIGN KEY (`FK_ref_atlas_id`) REFERENCES `brain_atlas` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `brain_region`
--

LOCK TABLES `brain_region` WRITE;
/*!40000 ALTER TABLE `brain_region` DISABLE KEYS */;
/*!40000 ALTER TABLE `brain_region` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cell_type`
--

LOCK TABLES `cell_type` WRITE;
/*!40000 ALTER TABLE `cell_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `cell_type` ENABLE KEYS */;
UNLOCK TABLES;

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
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_authentication_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_authentication_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=134 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=466 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

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
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `instance_name` (`instance_name`),
  UNIQUE KEY `slug` (`slug`),
  KEY `django_plotly_dash_dashapp_stateless_app_id_220444de_fk` (`stateless_app_id`),
  CONSTRAINT `django_plotly_dash_dashapp_stateless_app_id_220444de_fk` FOREIGN KEY (`stateless_app_id`) REFERENCES `django_plotly_dash_statelessapp` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_plotly_dash_dashapp`
--

LOCK TABLES `django_plotly_dash_dashapp` WRITE;
/*!40000 ALTER TABLE `django_plotly_dash_dashapp` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_plotly_dash_dashapp` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `app_name` (`app_name`),
  UNIQUE KEY `slug` (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_plotly_dash_statelessapp`
--

LOCK TABLES `django_plotly_dash_statelessapp` WRITE;
/*!40000 ALTER TABLE `django_plotly_dash_statelessapp` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_plotly_dash_statelessapp` ENABLE KEYS */;
UNLOCK TABLES;

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
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `django_site_domain_a2e37b91_uniq` (`domain`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_site`
--

LOCK TABLES `django_site` WRITE;
/*!40000 ALTER TABLE `django_site` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_site` ENABLE KEYS */;
UNLOCK TABLES;

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
  `injection_volume_ul` varchar(20) DEFAULT NULL,
  `FK_biosource_id` int(11) NOT NULL,
  `FK_performance_center_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `injection_FK_biosource_id_a64b7d48_fk_biosource_id` (`FK_biosource_id`),
  KEY `injection_FK_performance_cente_fa7018df_fk_authentic` (`FK_performance_center_id`),
  CONSTRAINT `injection_FK_biosource_id_a64b7d48_fk_biosource_id` FOREIGN KEY (`FK_biosource_id`) REFERENCES `biosource` (`id`),
  CONSTRAINT `injection_FK_performance_cente_fa7018df_fk_authentic` FOREIGN KEY (`FK_performance_center_id`) REFERENCES `auth_lab` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `injection`
--

LOCK TABLES `injection` WRITE;
/*!40000 ALTER TABLE `injection` DISABLE KEYS */;
/*!40000 ALTER TABLE `injection` ENABLE KEYS */;
UNLOCK TABLES;

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
  KEY `injection_virus_FK_injection_id_2781684a_fk_injection_id` (`FK_injection_id`),
  KEY `injection_virus_FK_virus_id_3f0ff6c1_fk_virus_id` (`FK_virus_id`),
  CONSTRAINT `injection_virus_FK_injection_id_2781684a_fk_injection_id` FOREIGN KEY (`FK_injection_id`) REFERENCES `injection` (`id`),
  CONSTRAINT `injection_virus_FK_virus_id_3f0ff6c1_fk_virus_id` FOREIGN KEY (`FK_virus_id`) REFERENCES `virus` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `injection_virus`
--

LOCK TABLES `injection_virus` WRITE;
/*!40000 ALTER TABLE `injection_virus` DISABLE KEYS */;
/*!40000 ALTER TABLE `injection_virus` ENABLE KEYS */;
UNLOCK TABLES;

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
  UNIQUE KEY `UK_session_xyz` (`FK_session_id`,`x`,`y`,`z`),
  KEY `FK_session_id` (`FK_session_id`),
  KEY `FK_cell_type_id` (`FK_cell_type_id`),
  CONSTRAINT `marked_cells_ibfk_1` FOREIGN KEY (`FK_session_id`) REFERENCES `annotation_session` (`id`),
  CONSTRAINT `marked_cells_ibfk_2` FOREIGN KEY (`FK_cell_type_id`) REFERENCES `cell_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `marked_cells`
--

LOCK TABLES `marked_cells` WRITE;
/*!40000 ALTER TABLE `marked_cells` DISABLE KEYS */;
/*!40000 ALTER TABLE `marked_cells` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=2223 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mouselight_neuron`
--

LOCK TABLES `mouselight_neuron` WRITE;
/*!40000 ALTER TABLE `mouselight_neuron` DISABLE KEYS */;
/*!40000 ALTER TABLE `mouselight_neuron` ENABLE KEYS */;
UNLOCK TABLES;

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
  `user_date` varchar(25) NOT NULL,
  `comments` varchar(255) NOT NULL,
  `FK_owner_id` int(11) DEFAULT NULL,
  `readonly` tinyint(1) NOT NULL,
  `active` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `neuroglancer_state_FK_owner_id_2bfff697_fk_auth_user_id` (`FK_owner_id`),
  CONSTRAINT `neuroglancer_state_FK_owner_id_2bfff697_fk_auth_user_id` FOREIGN KEY (`FK_owner_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `neuroglancer_state`
--

LOCK TABLES `neuroglancer_state` WRITE;
/*!40000 ALTER TABLE `neuroglancer_state` DISABLE KEYS */;
/*!40000 ALTER TABLE `neuroglancer_state` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `neuroglancer_urls`
--

DROP TABLE IF EXISTS `neuroglancer_urls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `neuroglancer_urls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `person_id` int(11) DEFAULT NULL,
  `url` longtext NOT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `readonly` tinyint(1) NOT NULL DEFAULT 0,
  `created` datetime(6) NOT NULL,
  `user_date` varchar(25) DEFAULT NULL,
  `comments` varchar(255) DEFAULT NULL,
  `updated` timestamp NOT NULL DEFAULT current_timestamp(),
  `vetted` int(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `K__NU` (`person_id`),
  CONSTRAINT `FK__NU_user_id` FOREIGN KEY (`person_id`) REFERENCES `auth_user` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=786 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `neuroglancer_urls`
--

LOCK TABLES `neuroglancer_urls` WRITE;
/*!40000 ALTER TABLE `neuroglancer_urls` DISABLE KEYS */;
/*!40000 ALTER TABLE `neuroglancer_urls` ENABLE KEYS */;
UNLOCK TABLES;

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
  CONSTRAINT `polygon_sequences_ibfk_1` FOREIGN KEY (`FK_session_id`) REFERENCES `annotation_session` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `polygon_sequences`
--

LOCK TABLES `polygon_sequences` WRITE;
/*!40000 ALTER TABLE `polygon_sequences` DISABLE KEYS */;
/*!40000 ALTER TABLE `polygon_sequences` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scan_run`
--

DROP TABLE IF EXISTS `scan_run`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `scan_run` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prep_id` varchar(200) NOT NULL,
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
  `converted_folder_path` varchar(200) DEFAULT NULL COMMENT 'the path to the slides folder on birdstore after convertion',
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
  `created` timestamp NULL DEFAULT current_timestamp(),
  `rescan_number` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK__scan_run_prep_id` (`prep_id`),
  CONSTRAINT `FK__scan_run_prep_id` FOREIGN KEY (`prep_id`) REFERENCES `animal` (`prep_id`)
) ENGINE=InnoDB AUTO_INCREMENT=45 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scan_run`
--

LOCK TABLES `scan_run` WRITE;
/*!40000 ALTER TABLE `scan_run` DISABLE KEYS */;
/*!40000 ALTER TABLE `scan_run` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `structure`
--

DROP TABLE IF EXISTS `structure`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `structure` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `abbreviation` varchar(25) NOT NULL,
  `description` longtext NOT NULL,
  `color` int(11) NOT NULL DEFAULT 100,
  `hexadecimal` char(7) DEFAULT NULL,
  `active` tinyint(1) NOT NULL,
  `created` datetime(6) NOT NULL,
  `is_structure` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `K__S_ABBREV` (`abbreviation`)
) ENGINE=InnoDB AUTO_INCREMENT=63 DEFAULT CHARSET=utf8mb3 COLLATE=utf8mb3_bin;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `structure`
--

LOCK TABLES `structure` WRITE;
/*!40000 ALTER TABLE `structure` DISABLE KEYS */;
/*!40000 ALTER TABLE `structure` ENABLE KEYS */;
UNLOCK TABLES;

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
  CONSTRAINT `structure_com_ibfk_1` FOREIGN KEY (`FK_session_id`) REFERENCES `annotation_session` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `structure_com`
--

LOCK TABLES `structure_com` WRITE;
/*!40000 ALTER TABLE `structure_com` DISABLE KEYS */;
/*!40000 ALTER TABLE `structure_com` ENABLE KEYS */;
UNLOCK TABLES;

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
) ENGINE=InnoDB AUTO_INCREMENT=82 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `viral_tracing_layer`
--

LOCK TABLES `viral_tracing_layer` WRITE;
/*!40000 ALTER TABLE `viral_tracing_layer` DISABLE KEYS */;
/*!40000 ALTER TABLE `viral_tracing_layer` ENABLE KEYS */;
UNLOCK TABLES;

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
  `label2` varchar(200) DEFAULT NULL,
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

--
-- Dumping data for table `virus`
--

LOCK TABLES `virus` WRITE;
/*!40000 ALTER TABLE `virus` DISABLE KEYS */;
/*!40000 ALTER TABLE `virus` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-03-10 12:24:35
