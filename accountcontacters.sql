/*
Navicat MariaDB Data Transfer



Target Server Type    : MariaDB
Target Server Version : 50556
File Encoding         : 65001

Date: 2018-10-29 15:24:11
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for accountcontacters
-- ----------------------------
DROP TABLE IF EXISTS `accountcontacters`;
CREATE TABLE `accountcontacters` (
  `arn` varchar(255) NOT NULL,
  `contactername` varchar(255) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `phonenum` varchar(20) DEFAULT NULL,
  `companyname` varchar(255) DEFAULT NULL,
  `departmentname` varchar(255) DEFAULT NULL,
  `account` varchar(255) DEFAULT NULL,
  `instancenum` int(11) NOT NULL,
  `aegistatus` int(11) NOT NULL DEFAULT '0',
  `updatetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`arn`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
