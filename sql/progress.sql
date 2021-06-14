-- MySQL dump 10.17  Distrib 10.3.25-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 192.168.1.12    Database: active_atlas_development
-- ------------------------------------------------------
-- Server version	10.3.25-MariaDB-0ubuntu0.20.04.1

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
-- Table structure for table `progress_lookup`
--

DROP TABLE IF EXISTS `progress_lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `progress_lookup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `description` text DEFAULT NULL,
  `script` varchar(200) DEFAULT NULL,
  `channel` int(11) NOT NULL,
  `action` varchar(25) NOT NULL,
  `downsample` tinyint(4) NOT NULL DEFAULT 1,
  `active` tinyint(4) NOT NULL DEFAULT 1,
  `created` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=256 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `progress_lookup`
--

LOCK TABLES `progress_lookup` WRITE;
/*!40000 ALTER TABLE `progress_lookup` DISABLE KEYS */;
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (10,'Slides are scanned','',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (20,'CZI files are placed on birdstore','',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (30,'CZI files are scanned to get metadata','create_meta.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (40,'QC is done on slides in web admin','',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (50,'CZI files are converted into tifs in DKXX/tif','create_tifs.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (55,'Full resolution numbered tifs are created in DKXX/preps/CH1/full','create_preps.py',0,'',1,1,'2020-12-28 16:19:37');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (60,'Downsampled numbered tifs are created in DKXX/preps/CH1/thumbnail','create_preps.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (70,'Create channel 1 histograms in DKXX/histogram','create_histogram.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (80,'Create thumbnail masks in DKXX/preps/thumbnail_masked','create_masks.py',0,'',1,1,'2020-07-10 14:22:24');

INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (90,'Create clean downsampled tifs with masks in DKXX/preps/CH1/thumbnail_cleaned','create_clean.py',1,'CLEAN',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (91,'Create clean downsampled tifs with masks in DKXX/preps/CH2/thumbnail_cleaned','create_clean.py',2,'CLEAN',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (92,'Create clean downsampled tifs with masks in DKXX/preps/CH3/thumbnail_cleaned','create_clean.py',3,'CLEAN',1,1,'2020-07-10 14:22:24');


INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (100,'Create aligned downsampled tifs with elastix to DKXX/preps/CH1/thumbnail_aligned','create_alignment.py',1,'ALIGN',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (101,'Create aligned downsampled tifs with elastix to DKXX/preps/CH2/thumbnail_aligned','create_alignment.py',2,'ALIGN',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (102,'Create aligned downsampled tifs with elastix to DKXX/preps/CH3/thumbnail_aligned','create_alignment.py',3,'ALIGN',1,1,'2020-07-10 14:22:24');


INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (110,'Create downsampled precomputed volumes in DKXX/neuroglancer_data/C1T','create_neuroglancer.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (120,'Create full resolution masks in DKXX/preps/full_masked','create_masks.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (130,'Full resolution numbered tifs are created in DKXX/preps/CH2/full','create_preps.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (140,'Downsampled numbered tifs are created in DKXX/preps/CH2/thumbnail','create_preps.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (150,'Create channel 2 histograms  in DKXX/histogram','create_histogram.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (160,'Downsampled numbered tifs are created in DKXX/preps/CH3/full','create_preps.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (170,'Downsampled numbered tifs are created in DKXX/preps/CH1/thumbnail','create_preps.py',0,'',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (180,'Create channel 3 histograms in DKXX/histogram','create_histogram.py',0,'',1,1,'2020-07-10 14:22:24');

INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (185,'Create clean full resolution tifs with masks in DKXX/preps/CH1/full_cleaned','create_clean.py',1,'CLEAN',0,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (190,'Create clean full resolution tifs with masks in DKXX/preps/CH2/full_cleaned','create_clean.py',2,'CLEAN',0,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (200,'Create clean full resolution tifs with masks in DKXX/preps/CH3/full_cleaned','create_clean.py',3,'CLEAN',0,1,'2020-07-10 14:22:24');

INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (209,'Create aligned full resolution tifs to DKXX/preps/CH1/full_aligned','create_alignment.py',1,'ALIGN',0,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (210,'Create aligned full resolution tifs to DKXX/preps/CH2/full_aligned','create_alignment.py',2,'ALIGN',0,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) 
VALUES (220,'Create aligned full resolution tifs to DKXX/preps/CH3/full_aligned','create_alignment.py',3,'ALIGN',0,1,'2020-07-10 14:22:24');

INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (225,'Low resolution in DKXX/neuroglancer_data/C1T','create_neuroglancer_image.py',1,'NEUROGLANCER',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (230,'Low resolution in DKXX/neuroglancer_data/C2T','create_neuroglancer_image.py',2,'NEUROGLANCER',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (240,'Low resolution in DKXX/neuroglancer_data/C3T','create_neuroglancer_image.py',3,'NEUROGLANCER',1,1,'2020-07-10 14:22:24');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (245,'Full resolution in DKXX/neuroglancer_data/C1','create_neuroglancer_image.py',1,'NEUROGLANCER',0,1,'2021-03-24 21:37:17');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (250,'Full resolution in DKXX/neuroglancer_data/C2','create_neuroglancer_image.py',2,'NEUROGLANCER',0,1,'2021-03-24 21:37:17');
INSERT INTO `progress_lookup` (`id`, `description`, `script`, `channel`, `action`, `downsample`, `active`, `created`) VALUES (255,'Full resolution in DKXX/neuroglancer_data/C3','create_neuroglancer_image.py',3,'NEUROGLANCER',0,1,'2021-03-24 21:37:17');
/*!40000 ALTER TABLE `progress_lookup` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-03-25  9:47:21
