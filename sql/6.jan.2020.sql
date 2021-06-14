-- MySQL dump 10.17  Distrib 10.3.25-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 192.168.1.12    Database: active_atlas_development
-- ------------------------------------------------------
-- Server version	10.4.17-MariaDB-log

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
-- Table structure for table `journals`
--

DROP TABLE IF EXISTS `journals`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `journals` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `prep_id` varchar(20) NOT NULL,
  `entry` longtext NOT NULL,
  `image` varchar(255) DEFAULT NULL,
  `issue_link` varchar(255) DEFAULT NULL,
  `created` timestamp NOT NULL DEFAULT current_timestamp(),
  `active` tinyint(4) NOT NULL DEFAULT 1,
  `completed` tinyint(4) NOT NULL DEFAULT 0,
  `person_id` int(11) NOT NULL,
  `problem_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `K__journals_prep_id` (`prep_id`),
  KEY `K__journals_person_id` (`person_id`),
  KEY `K__journals_problem_id` (`problem_id`),
  CONSTRAINT `FK__journals_person_id` FOREIGN KEY (`person_id`) REFERENCES `auth_user` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `FK__journals_prep_id` FOREIGN KEY (`prep_id`) REFERENCES `animal` (`prep_id`),
  CONSTRAINT `FK__journals_problem_id` FOREIGN KEY (`problem_id`) REFERENCES `problem_category` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `journals`
--

LOCK TABLES `journals` WRITE;
/*!40000 ALTER TABLE `journals` DISABLE KEYS */;
INSERT INTO `journals` VALUES (3,'DK52','Jan 4 2021\r\n\r\n1.Scene Image panel included scan of slide label in slides table slide 4 9256  scene index 18\r\n2.DK55_slide017_2020_09_25_9257 on the \"Slides\" database it has the incorrect scene indices which are out of order for some reason. \r\n\r\nEd - you were able to fix both issues- can you add a field to link to lines of code or whatever to indicate how you changed this- for a lab-book type of log of errors and fixes','static/images/journal/yb2Ei7M.jpg','','2021-01-06 04:18:37',1,1,2,1);
/*!40000 ALTER TABLE `journals` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `problem_category`
--

DROP TABLE IF EXISTS `problem_category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `problem_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `problem_category` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `problem_category`
--

LOCK TABLES `problem_category` WRITE;
/*!40000 ALTER TABLE `problem_category` DISABLE KEYS */;
INSERT INTO `problem_category` VALUES (1,'Intensity level problem'),(2,'Missing tissue');
/*!40000 ALTER TABLE `problem_category` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-01-06 17:00:46
