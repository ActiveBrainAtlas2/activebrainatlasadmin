-- MySQL dump 10.17  Distrib 10.3.22-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 192.168.1.12    Database: active_atlas_development
-- ------------------------------------------------------
-- Server version	5.7.27-log

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
-- Table structure for table `~jobs`
--

DROP TABLE IF EXISTS `~jobs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `~jobs` (
  `table_name` varchar(255) NOT NULL COMMENT 'className of the table',
  `key_hash` char(32) NOT NULL COMMENT 'key hash',
  `status` enum('reserved','error','ignore') NOT NULL COMMENT 'if tuple is missing, the job is available',
  `key` blob COMMENT 'structure containing the key',
  `error_message` varchar(2047) NOT NULL DEFAULT '' COMMENT 'error message returned if failed',
  `error_stack` blob COMMENT 'error stack if failed',
  `user` varchar(255) NOT NULL DEFAULT '' COMMENT 'database user',
  `host` varchar(255) NOT NULL DEFAULT '' COMMENT 'system hostname',
  `pid` int(10) unsigned NOT NULL DEFAULT '0' COMMENT 'system process id',
  `connection_id` bigint(20) unsigned NOT NULL DEFAULT '0' COMMENT 'connection_id()',
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'automatic timestamp',
  PRIMARY KEY (`table_name`,`key_hash`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='job reservation table for `active_atlas_development`';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `~jobs`
--

LOCK TABLES `~jobs` WRITE;
/*!40000 ALTER TABLE `~jobs` DISABLE KEYS */;
/*!40000 ALTER TABLE `~jobs` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-03-22 14:19:46
