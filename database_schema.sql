-- MySQL dump 10.13  Distrib 8.0.43, for Win64 (x86_64)
--
-- Host: localhost    Database: traffic
-- ------------------------------------------------------
-- Server version	8.0.43

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(80) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(120) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_admin` tinyint(1) DEFAULT '0',
  `email_verified` tinyint(1) DEFAULT '0',
  `verification_code` varchar(10) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `verification_code_expires` datetime DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `roads`
--

DROP TABLE IF EXISTS `roads`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roads` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `road_code` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `start_point` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `end_point` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `length` float DEFAULT NULL,
  `lanes` int DEFAULT NULL,
  `road_type` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `latitude_start` float DEFAULT NULL,
  `longitude_start` float DEFAULT NULL,
  `latitude_end` float DEFAULT NULL,
  `longitude_end` float DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `current_status_id` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_roads_road_code` (`road_code`),
  KEY `ix_roads_name` (`name`),
  KEY `fk_roads_current_status_id` (`current_status_id`),
  CONSTRAINT `fk_roads_current_status` FOREIGN KEY (`current_status_id`) REFERENCES `traffic_statuses` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roads`
--

LOCK TABLES `roads` WRITE;
/*!40000 ALTER TABLE `roads` DISABLE KEYS */;
INSERT INTO `roads` VALUES 
(1,'中山大道','ZSD001','市中心','东部新区',12.5,6,'主干道',NULL,NULL,NULL,NULL,'连接市中心与东部新区的主要干道','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(2,'人民路','RML001','南门','北门',8.3,6,'主干道',NULL,NULL,NULL,NULL,'市中心南北向主干道','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(3,'解放大道','JFDD001','东区','西区',15.2,8,'主干道',NULL,NULL,NULL,NULL,'城市东西向快速通道','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(4,'建设大道','JSDD001','火车站','机场',10.8,6,'主干道',NULL,NULL,NULL,NULL,'连接火车站与机场的主干道','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(5,'工农路','GNL001','工业区西','工业区东',9.5,6,'主干道',NULL,NULL,NULL,NULL,'工业区主要道路','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(6,'胜利街','SLJ001','商业区北','商业区南',5.2,4,'次干道',NULL,NULL,NULL,NULL,'商业区主要街道','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(7,'文化路','WHL001','文教区入口','文教区出口',6.8,4,'次干道',NULL,NULL,NULL,NULL,'文教区主干道','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(8,'幸福路','XFL001','小区A','小区D',4.5,4,'次干道',NULL,NULL,NULL,NULL,'居民区主要道路','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(9,'友谊大道','YYDD001','社区1','社区8',7.2,4,'次干道',NULL,NULL,NULL,NULL,'连接各大社区的次干道','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(10,'科技路','KJL001','高新区入口','高新区中心',5.9,4,'次干道',NULL,NULL,NULL,NULL,'高新区主要道路','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(11,'和平街','HPJ001','老城区西','老城区东',2.3,2,'支路',NULL,NULL,NULL,NULL,'老城区支路','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(12,'民主路','MZL001','民主广场','中山大道',1.8,2,'支路',NULL,NULL,NULL,NULL,'连接主干道的支路','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(13,'自由巷','ZYX001','居民楼A','居民楼F',1.2,2,'支路',NULL,NULL,NULL,NULL,'居民区内部道路','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(14,'富强街','FQJ001','商业街入口','商业街尾',2.1,2,'支路',NULL,NULL,NULL,NULL,'商业区支路','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(15,'文明路','WML001','学校门口','文化路',1.5,2,'支路',NULL,NULL,NULL,NULL,'学校周边道路','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(16,'环城快速路','HCKSL001','北环起点','北环终点',35.6,8,'快速路',NULL,NULL,NULL,NULL,'城市环线高架快速路','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(17,'滨江大道','BJDD001','江北','江南',22.4,6,'快速路',NULL,NULL,NULL,NULL,'沿江快速通道','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL),
(18,'机场高速','JCGS001','市区出口','机场入口',28.9,6,'快速路',NULL,NULL,NULL,NULL,'连接市区与机场的高速公路','2025-11-12 03:38:48','2025-11-12 03:38:48',NULL);
/*!40000 ALTER TABLE `roads` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `traffic_statuses`
--

DROP TABLE IF EXISTS `traffic_statuses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = uf8mb4 */;
CREATE TABLE `traffic_statuses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `road_id` int NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `speed` float DEFAULT NULL,
  `congestion_index` float DEFAULT NULL,
  `travel_time` int DEFAULT NULL,
  `vehicle_count` int DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `source` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_traffic_statuses_timestamp` (`timestamp`),
  KEY `ix_traffic_statuses_road_id` (`road_id`),
  KEY `idx_road_timestamp` (`road_id`,`timestamp`),
  CONSTRAINT `fk_traffic_statuses_road` FOREIGN KEY (`road_id`) REFERENCES `roads` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `traffic_events`
--

DROP TABLE IF EXISTS `traffic_events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `traffic_events` (
  `id` int NOT NULL AUTO_INCREMENT,
  `road_id` int NOT NULL,
  `event_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `severity` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `description` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `latitude` float DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'active',
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  `affected_lanes` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `source` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_traffic_events_start_time` (`start_time`),
  KEY `ix_traffic_events_road_id` (`road_id`),
  CONSTRAINT `fk_traffic_events_road` FOREIGN KEY (`road_id`) REFERENCES `roads` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `traffic_events`
--

LOCK TABLES `traffic_events` WRITE;
/*!40000 ALTER TABLE `traffic_events` DISABLE KEYS */;
INSERT INTO `traffic_events` VALUES 
(1,17,'交通管制','中','VIP车队通行,暂时封闭',NULL,NULL,'processing','2025-11-11 19:07:41',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(2,17,'交通管制','中','大型活动,临时交通管制',NULL,NULL,'active','2025-11-12 04:43:28',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(3,4,'施工','中','排水管道维护,单向通行',NULL,NULL,'active','2025-11-12 06:38:25',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(4,15,'交通管制','低','马拉松赛事,道路封闭',NULL,NULL,'active','2025-11-12 08:37:18',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(5,18,'其他','高','路边停车占道',NULL,NULL,'active','2025-11-12 08:40:48',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(6,18,'事故','中','轻微碰擦事故,车辆已移至路边',NULL,NULL,'active','2025-11-11 20:07:38',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(7,4,'其他','低','井盖丢失,已设置警示标志',NULL,NULL,'active','2025-11-11 12:27:59',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(8,14,'其他','高','路边停车占道',NULL,NULL,'active','2025-11-11 16:55:08',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(9,1,'事故','中','车辆故障抛锚,影响通行',NULL,NULL,'active','2025-11-11 21:41:42',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(10,10,'施工','中','地铁施工围挡,请绕行',NULL,NULL,'active','2025-11-12 10:17:04',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(11,11,'施工','中','地铁施工围挡,请绕行',NULL,NULL,'active','2025-11-12 06:20:32',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(12,4,'其他','中','路边停车占道',NULL,NULL,'processing','2025-11-12 01:04:09',NULL,NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(13,5,'其他','低','树木倒伏,正在清理',NULL,NULL,'resolved','2025-10-20 20:15:39','2025-10-20 23:54:47',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(14,10,'其他','高','路边停车占道',NULL,NULL,'resolved','2025-10-26 05:53:20','2025-10-26 10:39:30',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(15,18,'施工','低','道路维修施工,占用两条车道',NULL,NULL,'resolved','2025-11-11 10:28:14','2025-11-11 13:33:49',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(16,9,'交通管制','高','马拉松赛事,道路封闭',NULL,NULL,'resolved','2025-10-17 13:35:11','2025-10-17 18:14:02',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(17,7,'其他','高','路灯损坏,夜间请注意安全',NULL,NULL,'resolved','2025-11-09 18:36:39','2025-11-09 22:59:46',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(18,17,'其他','中','树木倒伏,正在清理',NULL,NULL,'resolved','2025-11-10 01:53:15','2025-11-10 08:11:26',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(19,5,'交通管制','中','消防演练,临时管制',NULL,NULL,'resolved','2025-11-09 13:09:49','2025-11-09 16:59:07',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(20,5,'恶劣天气','低','暴雨预警,建议延迟出行',NULL,NULL,'resolved','2025-10-20 02:38:28','2025-10-20 09:17:37',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(21,8,'事故','低','多车连环相撞,交警正在处理',NULL,NULL,'resolved','2025-10-22 18:04:36','2025-10-22 19:51:55',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(22,12,'施工','中','道路维修施工,占用两条车道',NULL,NULL,'resolved','2025-10-25 20:59:55','2025-10-26 04:40:03',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(23,5,'事故','高','车辆故障抛锚,影响通行',NULL,NULL,'resolved','2025-10-31 16:58:20','2025-10-31 21:08:56',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(24,15,'恶劣天气','中','大雾影响能见度,请谨慎驾驶',NULL,NULL,'resolved','2025-10-15 02:04:12','2025-10-15 11:47:48',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(25,15,'恶劣天气','中','大雨导致路面积水',NULL,NULL,'resolved','2025-11-06 10:17:11','2025-11-06 17:59:26',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(26,7,'事故','中','多车连环相撞,交警正在处理',NULL,NULL,'resolved','2025-11-08 05:26:24','2025-11-08 11:56:46',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(27,8,'事故','中','两车追尾事故,占用一条车道',NULL,NULL,'resolved','2025-11-05 04:45:04','2025-11-05 08:44:55',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(28,1,'事故','低','车辆故障抛锚,影响通行',NULL,NULL,'resolved','2025-10-25 23:58:12','2025-10-26 10:41:04',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(29,12,'恶劣天气','中','暴雨预警,建议延迟出行',NULL,NULL,'resolved','2025-10-28 20:00:57','2025-10-29 01:03:47',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(30,17,'恶劣天气','高','大雾影响能见度,请谨慎驾驶',NULL,NULL,'resolved','2025-11-07 08:04:22','2025-11-07 16:25:58',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(31,2,'事故','中','多车连环相撞,交警正在处理',NULL,NULL,'resolved','2025-10-18 13:53:31','2025-10-18 16:03:22',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(32,1,'其他','高','井盖丢失,已设置警示标志',NULL,NULL,'resolved','2025-10-27 07:14:50','2025-10-27 15:00:44',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(33,2,'交通管制','高','大型活动,临时交通管制',NULL,NULL,'resolved','2025-10-14 10:07:12','2025-10-14 20:35:23',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(34,16,'恶劣天气','高','路面结冰,车辆缓行',NULL,NULL,'resolved','2025-10-24 13:35:42','2025-10-24 18:13:50',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(35,17,'施工','中','排水管道维护,单向通行',NULL,NULL,'resolved','2025-11-02 11:23:24','2025-11-02 16:02:17',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(36,18,'恶劣天气','中','暴雨预警,建议延迟出行',NULL,NULL,'resolved','2025-11-02 06:18:53','2025-11-02 08:05:46',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48'),
(37,15,'其他','高','路灯损坏,夜间请注意安全',NULL,NULL,'resolved','2025-11-07 15:51:51','2025-11-08 01:21:22',NULL,NULL,'2025-11-12 03:38:48','2025-11-12 03:38:48');
/*!40000 ALTER TABLE `traffic_events` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `audit_logs`
--

DROP TABLE IF EXISTS `audit_logs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `audit_logs` (
  `id` int NOT NULL AUTO_INCREMENT,
  `table_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `record_id` int NOT NULL,
  `action` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `old_value` text COLLATE utf8mb4_unicode_ci,
  `new_value` text COLLATE utf8mb4_unicode_ci,
  `changed_at` datetime DEFAULT NULL,
  `changed_by` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT 'SYSTEM',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `weather_conditions`
--

DROP TABLE IF EXISTS `weather_conditions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `weather_conditions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `road_id` int DEFAULT NULL,
  `condition` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `temperature` float DEFAULT NULL,
  `visibility` float DEFAULT NULL,
  `precipitation` float DEFAULT NULL,
  `wind_speed` float DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_weather_conditions_timestamp` (`timestamp`),
  KEY `ix_weather_conditions_road_id` (`road_id`),
  CONSTRAINT `fk_weather_conditions_road` FOREIGN KEY (`road_id`) REFERENCES `roads` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `traffic_predictions`
--

DROP TABLE IF EXISTS `traffic_predictions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `traffic_predictions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `road_id` int NOT NULL,
  `predicted_time` datetime NOT NULL,
  `predicted_congestion` float DEFAULT NULL,
  `predicted_speed` float DEFAULT NULL,
  `confidence_score` float DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_traffic_predictions_predicted_time` (`predicted_time`),
  KEY `ix_traffic_predictions_road_id` (`road_id`),
  CONSTRAINT `fk_traffic_predictions_road` FOREIGN KEY (`road_id`) REFERENCES `roads` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `maintenance_schedules`
--

DROP TABLE IF EXISTS `maintenance_schedules`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `maintenance_schedules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `road_id` int NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `maintenance_type` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `impact_level` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'Planned',
  `description` text COLLATE utf8mb4_unicode_ci,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_maintenance_schedules_road_id` (`road_id`),
  CONSTRAINT `fk_maintenance_schedules_road` FOREIGN KEY (`road_id`) REFERENCES `roads` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-12-22 10:00:00
