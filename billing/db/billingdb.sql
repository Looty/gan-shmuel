--
-- Database: `billdb`
--

CREATE DATABASE IF NOT EXISTS `billdb`;
USE `billdb`;

-- --------------------------------------------------------

--
-- Table structure
--

CREATE TABLE IF NOT EXISTS `Provider` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM ;

CREATE TABLE IF NOT EXISTS `Rates` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `product_id` varchar(50) NOT NULL,
  `rate` int(11) DEFAULT 0,
  `scope` varchar(50) DEFAULT NULL,
  FOREIGN KEY (scope) REFERENCES `Provider`(`id`),
  PRIMARY KEY (`id`)
) ENGINE=MyISAM ;

CREATE TABLE IF NOT EXISTS `Trucks` (
  `id` varchar(10) NOT NULL UNIQUE,
  `provider_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  FOREIGN KEY (`provider_id`) REFERENCES `Provider`(`id`)
) ENGINE=MyISAM ;

INSERT IGNORE INTO Trucks (id,provider_id) VALUES ("1111111",1);
INSERT IGNORE INTO Trucks (id,provider_id) VALUES ("2222222",2);
INSERT IGNORE INTO Trucks (id,provider_id) VALUES ("3333333",1);
INSERT IGNORE INTO Trucks (id,provider_id) VALUES ("4444444",2);
INSERT IGNORE INTO Trucks (id,provider_id) VALUES ("5555555",1);
INSERT IGNORE INTO Trucks (id,provider_id) VALUES ("6666666",2);
