-- MySQL dump 10.17  Distrib 10.3.22-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: 192.168.1.12    Database: active_atlas_development
-- ------------------------------------------------------
-- Server version	10.4.12-MariaDB-log

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
-- Table structure for table `neuroglancer_urls`
--

DROP TABLE IF EXISTS `neuroglancer_urls`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `neuroglancer_urls` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `person_id` int(11) DEFAULT NULL,
  `url` longtext NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 0,
  `vetted` tinyint(1) NOT NULL DEFAULT 0,
  `created` datetime(6) NOT NULL,
  `user_date` varchar(25) DEFAULT NULL,
  `comments` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `K__NU` (`person_id`),
  CONSTRAINT `FK__NU_user_id` FOREIGN KEY (`person_id`) REFERENCES `auth_user` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `neuroglancer_urls`
--

LOCK TABLES `neuroglancer_urls` WRITE;
/*!40000 ALTER TABLE `neuroglancer_urls` DISABLE KEYS */;
INSERT INTO `neuroglancer_urls` VALUES (7,1,'{\"dimensions\":{\"x\":[4.6e-7,\"m\"],\"y\":[4.6e-7,\"m\"],\"z\":[0.00002,\"m\"]},\"position\":[27329.150390625,15196.357421875,259.5],\"crossSectionScale\":33.04210219855096,\"projectionScale\":29280.653629061802,\"layers\":[{\"type\":\"image\",\"source\":\"precomputed://https://activebrainatlas.ucsd.edu/data/MD589/neuroglancer_data/C1\",\"tab\":\"source\",\"name\":\"C1\"},{\"type\":\"segmentation\",\"source\":{\"url\":\"precomputed://https://activebrainatlas.ucsd.edu/data/MD589/neuroglancer_data/annotations\",\"transform\":{\"matrix\":[[0.8425645989798691,-0.32482450695003895,0.42913743280044525,20136.455950634867],[0.34463675427429896,0.9379247663884346,0.03328122892077513,6145.468433825321],[-0.41348077970635044,0.11990470713222026,0.9025832404941746,229.76310690536724]],\"outputDimensions\":{\"x\":[4.6e-7,\"m\"],\"y\":[4.6e-7,\"m\"],\"z\":[0.00002,\"m\"]},\"operations\":[61,62,63,0.5,25.5,15.5,1,1,1,1,20,0.5,5,0.01,0.1]}},\"tab\":\"source\",\"name\":\"annotations\"}],\"selectedLayer\":{\"layer\":\"annotations\",\"visible\":true},\"layout\":\"4panel\"}',1,0,'2020-08-03 14:45:02.202891','1596491100592','MD589 Full Res'),(14,1,'{\"dimensions\":{\"x\":[4.6e-7,\"m\"],\"y\":[4.6e-7,\"m\"],\"z\":[0.00002,\"m\"]},\"position\":[30440.5,17688.5,184.5],\"crossSectionScale\":69.40785183875524,\"projectionScale\":65536,\"layers\":[{\"type\":\"image\",\"source\":\"precomputed://https://activebrainatlas.ucsd.edu/data/DK52/neuroglancer_data/C1\",\"tab\":\"source\",\"shader\":\"#uicontrol float min slider(min=0, max=1, default=0)\\n#uicontrol float max slider(min=0, max=1, default=1)\\n#uicontrol float invert slider(min=0, max=1, default=0, step=1)\\n#uicontrol float brightness slider(min=-1, max=1)\\n#uicontrol float contrast slider(min=-3, max=3, step=0.01)\\n#uicontrol float gamma slider(min=0.05, max=2.5, default=1, step=0.05)\\n#uicontrol float linlog slider(min=0, max=1, default=0, step=1)\\n\\n  void main() {\\n    float limit = 40000.0;\\n    float pix = float(toRaw(getDataValue()));\\n\\n    if (linlog==1.0) {\\n    \\tpix = log(pix);\\n      \\tlimit = 10.0;\\n    } else {\\n    pix = pow(pix,gamma);\\n    limit = 40000.0;\\n    }\\n\\n\\n    float pix_val = pix/limit;\\n  \\tif(pix_val < min){\\n  \\t\\tpix_val = 0.0;\\n  \\t}\\n  \\tif(pix_val > max){\\n    \\tpix_val = 1.0;\\n  \\t}\\n\\n\\n  \\tif(invert==1.0){\\n  \\t  emitGrayscale((1.0 -( pix_val  - brightness)) * exp(contrast)) ;\\n  \\t}\\n  \\telse{\\n    \\temitGrayscale((pix_val + brightness) *\\n                  exp(contrast));\\n  \\t}\\n\\n}\\n\\n\",\"shaderControls\":{\"contrast\":0.96,\"gamma\":1.1},\"name\":\"C1\"}],\"selectedLayer\":{\"layer\":\"C1\",\"visible\":true},\"layout\":\"4panel\"}',1,0,'2020-08-04 12:04:20.175089','1596567858471','DK52 high res no annotations'),(15,1,'{\"dimensions\":{\"x\":[4.6e-7,\"m\"],\"y\":[4.6e-7,\"m\"],\"z\":[0.00002,\"m\"]},\"position\":[22715.5,14718.5,145.5],\"crossSectionScale\":33.04210219855096,\"projectionScale\":29280.653629061806,\"layers\":[{\"type\":\"image\",\"source\":\"precomputed://https://activebrainatlas.ucsd.edu/data/MD589/neuroglancer_data/C1\",\"tab\":\"source\",\"name\":\"C1\"},{\"type\":\"segmentation\",\"source\":{\"url\":\"precomputed://https://activebrainatlas.ucsd.edu/data/MD589/neuroglancer_data/annotations\",\"transform\":{\"matrix\":[[0.996,-0.087,0,20150.119],[0.087,0.996,0,7945.85],[0,0,1,95.349]],\"outputDimensions\":{\"x\":[4.6e-7,\"m\"],\"y\":[4.6e-7,\"m\"],\"z\":[0.00002,\"m\"]},\"operations\":[0,0,0,0,0,0,1,1,1,1,20,0.5,5,0.01,0.1]}},\"tab\":\"segments\",\"name\":\"annotations\"}],\"selectedLayer\":{\"layer\":\"annotations\",\"visible\":true},\"layout\":\"xy\"}',1,0,'2020-08-05 08:17:24.803973','1596640644632','MD589 w/annotations'),(16,1,'{\"dimensions\":{\"x\":[4.6e-7,\"m\"],\"y\":[4.6e-7,\"m\"],\"z\":[0.00002,\"m\"]},\"position\":[27329.150390625,15196.357421875,259.5],\"crossSectionScale\":33.04210219855096,\"projectionScale\":29280.653629061802,\"layers\":[{\"type\":\"image\",\"source\":\"precomputed://https://activebrainatlas.ucsd.edu/data/MD589/neuroglancer_data/C1\",\"tab\":\"source\",\"name\":\"C1\"},{\"type\":\"segmentation\",\"source\":{\"url\":\"precomputed://https://activebrainatlas.ucsd.edu/data/MD589/neuroglancer_data/annotations\",\"transform\":{\"matrix\":[[0.8425645989798691,-0.32482450695003895,0.42913743280044525,20396.455950634867],[0.34463675427429896,0.9379247663884346,0.03328122892077513,6145.468433825321],[-0.41348077970635044,0.11990470713222026,0.9025832404941746,229.76310690536724]],\"outputDimensions\":{\"x\":[4.6e-7,\"m\"],\"y\":[4.6e-7,\"m\"],\"z\":[0.00002,\"m\"]},\"operations\":[321,62,63,0.5,25.5,15.5,1,1,1,1,20,0.5,5,0.01,0.1]}},\"tab\":\"source\",\"name\":\"annotations\"}],\"selectedLayer\":{\"layer\":\"annotations\",\"visible\":true},\"layout\":\"4panel\"}',0,0,'2020-08-05 13:11:40.009890','1596658298757','MD589 some changes'),(17,1,'kjhlkjh',1,0,'2020-08-09 11:11:32.696183','lkjhlkjh','lkjhlkjh'),(18,1,'kjhlkjh',1,0,'2020-08-09 11:19:03.042063','lkjhlkjh','lkjhlkjh'),(19,1,'asldkfja;slkjfd',1,0,'2020-08-09 11:19:28.520109','11111111111111','hey you!!!!!!!'),(20,1,'lkj;lj',1,0,'2020-08-10 15:36:28.554244','lkj;lkj;lkj','66666666666666666');
/*!40000 ALTER TABLE `neuroglancer_urls` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-08-11 10:04:16
