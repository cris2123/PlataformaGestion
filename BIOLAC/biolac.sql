-- MySQL dump 10.16  Distrib 10.1.17-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: biolac
-- ------------------------------------------------------
-- Server version	10.1.17-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `biolac`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `biolac` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `biolac`;

--
-- Table structure for table `courseBudgetItems`
--

DROP TABLE IF EXISTS `courseBudgetItems`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `courseBudgetItems` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `budget_desc` varchar(120) DEFAULT NULL,
  `budget_value` varchar(10) DEFAULT NULL,
  `curso_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `curso_id` (`curso_id`),
  CONSTRAINT `courseBudgetItems_ibfk_1` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courseBudgetItems`
--

LOCK TABLES `courseBudgetItems` WRITE;
/*!40000 ALTER TABLE `courseBudgetItems` DISABLE KEYS */;
INSERT INTO `courseBudgetItems` VALUES (1,'dffsfdssdf','dsfsdf',1);
/*!40000 ALTER TABLE `courseBudgetItems` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courseCollaborators`
--

DROP TABLE IF EXISTS `courseCollaborators`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `courseCollaborators` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `coll_name` varchar(20) DEFAULT NULL,
  `coll_position` varchar(20) DEFAULT NULL,
  `coll_institution` varchar(30) DEFAULT NULL,
  `coll_phone` varchar(20) DEFAULT NULL,
  `coll_fax` varchar(26) DEFAULT NULL,
  `coll_email` varchar(70) DEFAULT NULL,
  `coll_area` varchar(15) DEFAULT NULL,
  `coll_cv` varchar(100) DEFAULT NULL,
  `curso_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `curso_id` (`curso_id`),
  CONSTRAINT `courseCollaborators_ibfk_1` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courseCollaborators`
--

LOCK TABLES `courseCollaborators` WRITE;
/*!40000 ALTER TABLE `courseCollaborators` DISABLE KEYS */;
INSERT INTO `courseCollaborators` VALUES (1,'ddffsfdsfs','Head','fsfsfsfs','0412=7256957','0123-234-56-78','cristhian8bravo@gmail.com','Master','Probando path',1),(2,'sdfsdfsfsfsd','gfdgfgfdgfdg','gfgdfgdgdfd','dljdgfdgd','dggjhjhgfhdf','gfdgfdgdfgdf','dfgdfgdgfgdffd','Probando path',1);
/*!40000 ALTER TABLE `courseCollaborators` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `courseObjectives`
--

DROP TABLE IF EXISTS `courseObjectives`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `courseObjectives` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `objective_item` varchar(200) NOT NULL,
  `curso_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `curso_id` (`curso_id`),
  CONSTRAINT `courseObjectives_ibfk_1` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `courseObjectives`
--

LOCK TABLES `courseObjectives` WRITE;
/*!40000 ALTER TABLE `courseObjectives` DISABLE KEYS */;
INSERT INTO `courseObjectives` VALUES (1,'sdsdsfsdfdfd',1),(2,'fsdfdfsdff',1);
/*!40000 ALTER TABLE `courseObjectives` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `curso`
--

DROP TABLE IF EXISTS `curso`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `curso` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `priority1` tinyint(1) DEFAULT NULL,
  `priority2` tinyint(1) DEFAULT NULL,
  `priority3` tinyint(1) DEFAULT NULL,
  `courseTitle` varchar(80) DEFAULT NULL,
  `hostname` varchar(80) DEFAULT NULL,
  `hostAddress` varchar(80) DEFAULT NULL,
  `coordName` varchar(80) DEFAULT NULL,
  `coordTitle` varchar(80) DEFAULT NULL,
  `coordAffiliation` varchar(80) DEFAULT NULL,
  `commDate` datetime NOT NULL,
  `termDate` datetime NOT NULL,
  `courseDescription` varchar(2000) DEFAULT NULL,
  `organizationTrainingDescription` varchar(2000) DEFAULT NULL,
  `courseTrainees` varchar(2000) DEFAULT NULL,
  `status_aprobado` tinyint(1) DEFAULT NULL,
  `status_revisado` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `curso`
--

LOCK TABLES `curso` WRITE;
/*!40000 ALTER TABLE `curso` DISABLE KEYS */;
INSERT INTO `curso` VALUES (1,1,1,1,'dsdsds','','El cafetal','Josefo','Master','Americas','2016-08-08 00:00:00','2016-08-08 00:00:00','sfdsfsdfdfs','fsdfdsfdfsdfsfd','sfsdfsfs',0,0);
/*!40000 ALTER TABLE `curso` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documentos_cursos`
--

DROP TABLE IF EXISTS `documentos_cursos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `documentos_cursos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(80) DEFAULT NULL,
  `path` varchar(100) DEFAULT NULL,
  `hashed_name` varchar(100) DEFAULT NULL,
  `fecha` datetime DEFAULT NULL,
  `curso_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `curso_id` (`curso_id`),
  CONSTRAINT `documentos_cursos_ibfk_1` FOREIGN KEY (`curso_id`) REFERENCES `curso` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documentos_cursos`
--

LOCK TABLES `documentos_cursos` WRITE;
/*!40000 ALTER TABLE `documentos_cursos` DISABLE KEYS */;
INSERT INTO `documentos_cursos` VALUES (1,'Catherine_Paquet,_Diane_Teare_Building_Scalable_Cisco_Networks_Prepare_for_CCNP_','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12_WiZxsBfCTcVfZ08PVVbruQ1vyquybWN.2XPDP.EP','b\'$2b$12$/WiZxsBfCTcVfZ08PVVbruQ1vyquybWN.2XPDP.EPr.V91JfebxQu\'','2016-09-24 02:29:00',1),(2,'bonitasoft-customdevprocess_300516_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12v.wKN96W8G4cQEfeq3i0Ae6DZy2jm4eVo8Y7QTHkP','b\'$2b$12$v.wKN96W8G4cQEfeq3i0Ae6DZy2jm4eVo8Y7QTHkPJPuGXN3rFLt.\'','2016-09-24 02:29:00',1);
/*!40000 ALTER TABLE `documentos_cursos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fellow`
--

DROP TABLE IF EXISTS `fellow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fellow` (
  `id` int(11) NOT NULL,
  `name` varchar(30) DEFAULT NULL,
  `priority1` tinyint(1) DEFAULT NULL,
  `priority2` tinyint(1) DEFAULT NULL,
  `priority3` tinyint(1) DEFAULT NULL,
  `fellowTitle` varchar(40) DEFAULT NULL,
  `destination` varchar(50) DEFAULT NULL,
  `generalObjective` varchar(300) DEFAULT NULL,
  `justification` varchar(300) DEFAULT NULL,
  `methodology` varchar(300) DEFAULT NULL,
  `workingPlan` varchar(400) DEFAULT NULL,
  `status_aprobado` tinyint(1) DEFAULT NULL,
  `creation_date` datetime NOT NULL,
  `revisiones_completadas` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fellow`
--

LOCK TABLES `fellow` WRITE;
/*!40000 ALTER TABLE `fellow` DISABLE KEYS */;
INSERT INTO `fellow` VALUES (1,'Cristhian',1,1,1,'Probando usuarios fellow ','Madrid','Probando y agregando fellows dummy users ','Mira como logro poner los fellow ','Mira como logro usar otro fello ','Poniendo fellow ',0,'2016-09-25 07:16:34',0),(3,'Jaime',1,1,1,'Probando fellows2 ','Francia ','Mirando como se puede hacer esto ','Observando el mar y mas alla ','Que tal van quedando los cursos ','Que tal se ven los cursos ',0,'2016-09-25 07:26:24',0);
/*!40000 ALTER TABLE `fellow` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fellowActivities`
--

DROP TABLE IF EXISTS `fellowActivities`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fellowActivities` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `activity_item` varchar(100) NOT NULL,
  `fellow_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fellow_id` (`fellow_id`),
  CONSTRAINT `fellowActivities_ibfk_1` FOREIGN KEY (`fellow_id`) REFERENCES `fellow` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fellowActivities`
--

LOCK TABLES `fellowActivities` WRITE;
/*!40000 ALTER TABLE `fellowActivities` DISABLE KEYS */;
INSERT INTO `fellowActivities` VALUES (1,'Probando como hacer las cosas bien',1),(2,'Probando como hacer las cosas bien ',1),(3,'Mirando como se ve ',3),(4,'Mirando como se ve2 ',3);
/*!40000 ALTER TABLE `fellowActivities` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fellowDocuments`
--

DROP TABLE IF EXISTS `fellowDocuments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fellowDocuments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) DEFAULT NULL,
  `path` varchar(100) DEFAULT NULL,
  `hashed_name` varchar(100) DEFAULT NULL,
  `fecha` datetime DEFAULT NULL,
  `fellow_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fellow_id` (`fellow_id`),
  CONSTRAINT `fellowDocuments_ibfk_1` FOREIGN KEY (`fellow_id`) REFERENCES `fellow` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fellowDocuments`
--

LOCK TABLES `fellowDocuments` WRITE;
/*!40000 ALTER TABLE `fellowDocuments` DISABLE KEYS */;
INSERT INTO `fellowDocuments` VALUES (1,'10.1.1.724.6954_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12Kc7f9kNUgU_qhu035QQCK.B_wsxUdOiHNWdRYEy6R','b\'$2b$12$Kc7f9kNUgU/qhu035QQCK.B/wsxUdOiHNWdRYEy6R6dIOQjuojeRS\'','2016-09-25 07:16:34',1),(2,'bonitasoft-customdevprocess_300516_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12FjTZshF4XBHJ7mKrHRuHLu3mzB_JyJXujOUeMsav4','b\'$2b$12$FjTZshF4XBHJ7mKrHRuHLu3mzB/JyJXujOUeMsav4r4vMkFtgbUYe\'','2016-09-25 07:16:34',1),(3,'Brent_Stewart_CCNP_BSCI_Official_Exam_Certification_Guide_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12Q6CPtjIwwPFQf0xBApDOqe5Hxpxl4Prws6kBZOZdy','b\'$2b$12$Q6CPtjIwwPFQf0xBApDOqe5Hxpxl4Prws6kBZOZdyzWKkrZ51Xo6u\'','2016-09-25 07:16:34',1),(4,'comprobante sept-dic 2016_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12Zt4daP9GB0pBjldoZiC7Ce7JI4KUn7a990Zps.H0I','b\'$2b$12$Zt4daP9GB0pBjldoZiC7Ce7JI4KUn7a990Zps.H0IkzkG.QTqg5pG\'','2016-09-25 07:16:35',1),(5,'Freeman_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12q7nICY1SnbEE3hDaWRy4dOZdcxcxbWyMwyl03HgS0','b\'$2b$12$q7nICY1SnbEE3hDaWRy4dOZdcxcxbWyMwyl03HgS0mV/YtRDplC0i\'','2016-09-25 07:16:35',1),(6,'IV2008_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12ORCs8tlY54.QtpliTknGvORiSs8iAZdeKho0EDi2f','b\'$2b$12$ORCs8tlY54.QtpliTknGvORiSs8iAZdeKho0EDi2frDkacQLWy10K\'','2016-09-25 07:16:35',1),(7,'MasteringIO_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12UyJ7ecS08Lv7Gk3MY_hb.uCu3Kd5n.Oi4JhJAtczr','b\'$2b$12$UyJ7ecS08Lv7Gk3MY/hb.uCu3Kd5n.Oi4JhJAtczrfLL7PYAR1BJ2\'','2016-09-25 07:16:35',1),(8,'nRF51822_Evaluation_Kit User_Guide v1.2_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12_ZtOcl7ve90m4_q.OTMPIuGSsZGfawDc7oA5EDksB','b\'$2b$12$/ZtOcl7ve90m4/q.OTMPIuGSsZGfawDc7oA5EDksBjlMsoqW7FpVO\'','2016-09-25 07:16:35',1),(9,'cisco-ccnp_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12H_R0I7VJQ4ciVypXaCLolOeGlkcu0rnar3029HIU1','b\'$2b$12$H/R0I7VJQ4ciVypXaCLolOeGlkcu0rnar3029HIU1OOtggK.CYJUq\'','2016-09-25 07:16:35',1),(10,'Cap 1 autoregulacion_user_1pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12joRRqO.3F5WMmCV5R63uuuyUH1Xco3CxPkDg1RCb9','b\'$2b$12$joRRqO.3F5WMmCV5R63uuuyUH1Xco3CxPkDg1RCb9BMEiIpLrLO0m\'','2016-09-25 07:16:35',1),(11,'bonitasoft-customdevprocess_300516_user_3pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12OnXNiAibzvy5SGlNDnNy0uchws0_zWIykEV14EfHX','b\'$2b$12$OnXNiAibzvy5SGlNDnNy0uchws0/zWIykEV14EfHXuLtBlIdb6qyq\'','2016-09-25 07:26:24',3),(12,'Brent_Stewart_CCNP_BSCI_Official_Exam_Certification_Guide_user_3pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12esqhzdoJAGj1kRPG3i4GAO4Bp6M.QUQbCYAa9JGiq','b\'$2b$12$esqhzdoJAGj1kRPG3i4GAO4Bp6M.QUQbCYAa9JGiqz2NT.B/nKynC\'','2016-09-25 07:26:24',3),(13,'Cap 1 autoregulacion_user_3pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12ygYtptXAmAfcKA71K9ROw.YV3K.MzFWsNYdaSzSK5','b\'$2b$12$ygYtptXAmAfcKA71K9ROw.YV3K.MzFWsNYdaSzSK5UUqe.HNgn2l6\'','2016-09-25 07:26:24',3),(14,'Brent_Stewart_CCNP_BSCI_Official_Exam_Certification_Guide_user_3pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12KJqeHPW.f5V9sTnk8yBaaOFmTyPDBmH5HQBojTYor','b\'$2b$12$KJqeHPW.f5V9sTnk8yBaaOFmTyPDBmH5HQBojTYorqcVauSvOI5zq\'','2016-09-25 07:26:24',3),(15,'nRF51822_Evaluation_Kit User_Guide v1.2_user_3pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12tgI6AHllkrd8ruStMZlNkeOtXohf0344jx0HBDSA8','b\'$2b$12$tgI6AHllkrd8ruStMZlNkeOtXohf0344jx0HBDSA8dNc94ubKm.Wy\'','2016-09-25 07:26:24',3),(16,'MasteringIO_user_3pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12rBsvftDQAHNnop_c_RMItuxV6JoMD5DhNqvBTSIBS','b\'$2b$12$rBsvftDQAHNnop/c/RMItuxV6JoMD5DhNqvBTSIBS/KqA2cIVOdK2\'','2016-09-25 07:26:24',3),(17,'IV2008_user_3pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12v.xDa3KmD3vwf2EpYiaAeecSfN9dlGP_KchHbkWCt','b\'$2b$12$v.xDa3KmD3vwf2EpYiaAeecSfN9dlGP/KchHbkWCtohEGN4x6lar.\'','2016-09-25 07:26:24',3),(18,'Freeman_user_3pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b126eFGHafb38MDAn59y0wKsu.DJo8p8BG.L7su2XRXJ','b\'$2b$12$6eFGHafb38MDAn59y0wKsu.DJo8p8BG.L7su2XRXJVmQ154Vj0sPO\'','2016-09-25 07:26:24',3),(19,'10.1.1.724.6954_user_3pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12EmxX1A334OFsU1HLSasr7.V3DnlXPaC2J8r5L6XWs','b\'$2b$12$EmxX1A334OFsU1HLSasr7.V3DnlXPaC2J8r5L6XWsrPBZW8BvX4fm\'','2016-09-25 07:26:24',3),(20,'cisco-ccnp_user_3pdf','/home/cris1/ominia/miscellaneos/BIOLAC/static/uploads/b2b12j57IkxnOzbkLo4GS1H8YGOdlci8wJKS_4gAHg6JL3','b\'$2b$12$j57IkxnOzbkLo4GS1H8YGOdlci8wJKS/4gAHg6JL33gQqR139pLae\'','2016-09-25 07:26:24',3);
/*!40000 ALTER TABLE `fellowDocuments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `fellowObjectives`
--

DROP TABLE IF EXISTS `fellowObjectives`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `fellowObjectives` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `objective_item` varchar(200) NOT NULL,
  `fellow_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fellow_id` (`fellow_id`),
  CONSTRAINT `fellowObjectives_ibfk_1` FOREIGN KEY (`fellow_id`) REFERENCES `fellow` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `fellowObjectives`
--

LOCK TABLES `fellowObjectives` WRITE;
/*!40000 ALTER TABLE `fellowObjectives` DISABLE KEYS */;
INSERT INTO `fellowObjectives` VALUES (1,'Probando fellows1 ',1),(2,'Probando fellows2',1),(3,'probando1',3),(4,'probando2',3);
/*!40000 ALTER TABLE `fellowObjectives` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permisos`
--

DROP TABLE IF EXISTS `permisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `permisos` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(15) DEFAULT NULL,
  `description` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permisos`
--

LOCK TABLES `permisos` WRITE;
/*!40000 ALTER TABLE `permisos` DISABLE KEYS */;
INSERT INTO `permisos` VALUES (1,'Ver cursos','Permite a los usuarios ver los cursos disponibles'),(2,'Ver historial','Permite observar el historial de las personas'),(3,'Editar cursos','Permite editar las solicitudes de los cursos '),(4,'Editar becarios','Permite editar las solicitudes de los becarios');
/*!40000 ALTER TABLE `permisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(15) NOT NULL,
  `description` varchar(80) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'estandar','usuarios normales entran con este rol'),(2,'evaluadores','Usuarios que pueden evaluar a los concursantes'),(3,'admin','Usuario con todos los permisos de la aplicacion'),(4,'asistentes','Usuario con menos permisos que los admin');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `rolepermisos`
--

DROP TABLE IF EXISTS `rolepermisos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `rolepermisos` (
  `role_id` int(11) DEFAULT NULL,
  `permisos_id` int(11) DEFAULT NULL,
  KEY `role_id` (`role_id`),
  KEY `permisos_id` (`permisos_id`),
  CONSTRAINT `rolepermisos_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`),
  CONSTRAINT `rolepermisos_ibfk_2` FOREIGN KEY (`permisos_id`) REFERENCES `permisos` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `rolepermisos`
--

LOCK TABLES `rolepermisos` WRITE;
/*!40000 ALTER TABLE `rolepermisos` DISABLE KEYS */;
INSERT INTO `rolepermisos` VALUES (1,1),(2,1),(2,4),(3,1),(3,2),(3,3),(3,4),(4,1),(4,2),(4,3);
/*!40000 ALTER TABLE `rolepermisos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(80) DEFAULT NULL,
  `name` varchar(20) NOT NULL,
  `lastname` varchar(20) NOT NULL,
  `birth_date` datetime NOT NULL,
  `citizenship` varchar(25) NOT NULL,
  `gender` varchar(25) NOT NULL,
  `marital_status` varchar(15) NOT NULL,
  `profile_picture` varchar(100) DEFAULT NULL,
  `country` varchar(20) NOT NULL,
  `city` varchar(20) NOT NULL,
  `zip_code` int(11) NOT NULL,
  `address` varchar(50) NOT NULL,
  `phonenumber` varchar(25) NOT NULL,
  `cellphone` varchar(25) NOT NULL,
  `institution` varchar(35) NOT NULL,
  `faculty` varchar(20) NOT NULL,
  `section` varchar(20) NOT NULL,
  `max_academic_level` varchar(20) NOT NULL,
  `current_academic_level` varchar(20) NOT NULL,
  `work_place` varchar(30) NOT NULL,
  `possible_evaluator` tinyint(1) DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `role_id` int(11) DEFAULT NULL,
  `password` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'cristhian3bravo@gmail.com','Cristhian','Bravo','2016-09-24 02:27:09','Venezolano','Hombre','single','/data','venezuela','Caracas',1061,'El cafetal','0212-9858996','0412-7256957','USB','algo','algo','bachiller','bachiller','usb',0,1,1,'pbkdf2:sha1:1000$28XTEUBE$6dd3cd8eb19d500bb727f28ca768c459b3e65edb'),(2,'cristhian4bravo@gmail.com','andres','fernandez','2016-08-08 00:00:00','venezolano','Hombre','Soltero','','Venezuela','caracas',1061,'El cafetal . Av circunvalacion del sol','0212-9858996','0412-7256957','USB','ingenerieria','Electronica','bachiller','universidad','USB',0,1,2,'pbkdf2:sha1:1000$eAtDDxi9$287c0ba946705ad6b91a891e1fe217d7cb856678'),(3,'cristhian5bravo@gmail.com','Jaime','a','2016-08-08 00:00:00','venezolano','Hombre','Soltero','','venezuela','caracas',1061,'El cafetal . Av circunvalacion del sol','0212-9858996','0412-7256957','USB','ingenerieria','Electronica','bachiller','universidad','USB',0,1,1,'pbkdf2:sha1:1000$ngHq2K4J$12693637d9c028f8be76ccf2bd3fb61769fcc159'),(4,'cristhian6bravo@gmail.com','Cameron','Bravo','2016-08-08 00:00:00','venezolano','Hombre','Soltero','','venezuela','caracas',1061,'El cafetal . Av circunvalacion del sol','0212-9858996','0412-7256957','USB','ingenerieria','Electronica','bachiller','universidad','USB',0,1,3,'pbkdf2:sha1:1000$do1rO2Bz$3c22c0b3cfd0ecc201f3426f29bab6666b8bed5d');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-09-25  8:05:51
