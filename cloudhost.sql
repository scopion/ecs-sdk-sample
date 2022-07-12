/*
Navicat MariaDB Data Transfer



Target Server Type    : MariaDB
Target Server Version : 50556
File Encoding         : 65001

Date: 2018-10-29 15:24:38
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for cloudhost
-- ----------------------------
DROP TABLE IF EXISTS `cloudhost`;
CREATE TABLE `cloudhost` (
  `instanceId` varchar(64) NOT NULL,
  `instanceName` varchar(128) DEFAULT NULL,
  `privateIpAddress` varchar(32) DEFAULT NULL,
  `publicIpAddress` varchar(32) DEFAULT NULL,
  `eipAddress` varchar(32) DEFAULT NULL,
  `OSNEnvironment` varchar(32) NOT NULL,
  `OSName` varchar(64) DEFAULT NULL,
  `regionId` varchar(16) NOT NULL,
  `serialNumber` varchar(64) DEFAULT NULL,
  `updateTime` datetime DEFAULT NULL,
  `status` varchar(16) NOT NULL,
  `arn` varchar(255) NOT NULL,
  PRIMARY KEY (`instanceId`),
  KEY `arn` (`arn`),
  CONSTRAINT `cloudhost_ibfk_1` FOREIGN KEY (`arn`) REFERENCES `accountcontacters` (`arn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
