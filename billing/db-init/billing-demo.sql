-- First, your original schema creation SQL
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
) ENGINE=MyISAM AUTO_INCREMENT=10001 ;

CREATE TABLE IF NOT EXISTS `Rates` (
`product_id` varchar(50) NOT NULL,
`rate` int(11) DEFAULT 0,
`scope` varchar(50) DEFAULT NULL,
FOREIGN KEY (scope) REFERENCES `Provider`(`id`)
) ENGINE=MyISAM ;

CREATE TABLE IF NOT EXISTS `Trucks` (
`id` varchar(10) NOT NULL,
`provider_id` int(11) DEFAULT NULL,
PRIMARY KEY (`id`),
FOREIGN KEY (`provider_id`) REFERENCES `Provider`(`id`)
) ENGINE=MyISAM ;

-- Then, append the data insertion SQL I provided
-- Populate Provider table
INSERT INTO `Provider` (`id`, `name`) VALUES
(10001, 'FastFreight Logistics'),
(10002, 'Highway Express'),
(10003, 'Reliable Transit'),
(10004, 'Blue Ridge Transport'),
(10005, 'Valley Shipping Co.');

-- Populate Trucks table
INSERT INTO `Trucks` (`id`, `provider_id`) VALUES
-- FastFreight Logistics trucks
('T-14409', 10001),
('T-16474', 10001),
('T-14964', 10001),
('T-17194', 10001),
('T-17250', 10001),
('T-14045', 10001),
('T-14263', 10001),

-- Highway Express trucks
('T-17164', 10002),
('T-16810', 10002),
('T-17077', 10002),
('T-13972', 10002),
('T-13982', 10002),
('T-15689', 10002),

-- Reliable Transit trucks
('T-14664', 10003),
('T-14623', 10003),
('T-14873', 10003),
('T-14064', 10003),
('T-13799', 10003),
('T-15861', 10003),
('T-16584', 10003),
('T-17267', 10003),

-- Blue Ridge Transport trucks
('T-16617', 10004),
('T-16270', 10004),
('T-14969', 10004),
('T-15521', 10004),
('T-16556', 10004),

-- Valley Shipping Co. trucks
('T-17744', 10005),
('T-17412', 10005),
('T-15733', 10005),
('T-14091', 10005),
('T-14129', 10005);

-- Populate Rates table
INSERT INTO `Rates` (`product_id`, `rate`, `scope`) VALUES
-- General rates for all providers
('Navel', 93, 'All'),
('Blood', 112, 'All'),
('Mandarin', 104, 'All'),
('Shamuti', 84, 'All'),
('Tangerine', 92, 'All'),
('Clementine', 113, 'All'),
('Grapefruit', 88, 'All'),
('Valencia', 87, 'All'),
('orange', 80, 'All'),

-- Provider-specific rates
('Mandarin', 102, 10003),
('Mandarin', 120, 10004),
('Tangerine', 85, 10002),
('Valencia', 90, 10004);
