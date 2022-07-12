-- --------------------------------------------------------
-- 主机:                           0
-- 服务器版本:                        5.5.56-MariaDB - MariaDB Server
-- 服务器操作系统:                      Linux
-- HeidiSQL 版本:                  9.4.0.5125
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

-- 导出  表 talscan.cloudhost 结构
CREATE TABLE IF NOT EXISTS `cloudhost` (
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

-- 数据导出被取消选择。
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
