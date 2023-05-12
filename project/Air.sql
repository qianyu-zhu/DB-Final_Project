-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- 主机： localhost
-- 生成日期： 2023-05-07 16:30:07
-- 服务器版本： 10.4.27-MariaDB
-- PHP 版本： 8.0.25

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `Air`
--

-- --------------------------------------------------------

--
-- 表的结构 `airline`
--

CREATE TABLE `airline` (
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `airline`
--

INSERT INTO `airline` (`airline_name`) VALUES
('All Nippon Airways'),
('American Airline'),
('Eastern Airline'),
('Southern Airline');

-- --------------------------------------------------------

--
-- 表的结构 `airline_staff`
--

CREATE TABLE `airline_staff` (
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL,
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `airline_staff`
--

INSERT INTO `airline_staff` (`username`, `password`, `first_name`, `last_name`, `date_of_birth`, `airline_name`) VALUES
('Staff001', 'b59c67bf196a4758191e42f76670ceba', 'Lihua', 'Xu', '1999-06-23', 'All Nippon Airways'),
('Staff002', 'b59c67bf196a4758191e42f76670ceba', 'Roberto', 'Fernandez', '1950-01-01', 'American Airline'),
('Staff003', 'b59c67bf196a4758191e42f76670ceba', 'Wei', 'Wu', '1982-06-23', 'Eastern Airline'),
('Staff004', 'b59c67bf196a4758191e42f76670ceba', 'Yuning', 'Liu', '1980-01-01', 'Southern Airline'),
('Staff005', 'b59c67bf196a4758191e42f76670ceba', 'Chen', 'Chen', '1990-02-14', 'American Airline'),
('Staff007', 'b59c67bf196a4758191e42f76670ceba', 'James', 'Bond', '1990-02-02', 'American Airline');

-- --------------------------------------------------------

--
-- 表的结构 `airplane`
--

CREATE TABLE `airplane` (
  `airline_name` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL,
  `seats` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `airplane`
--

INSERT INTO `airplane` (`airline_name`, `airplane_id`, `seats`) VALUES
('All Nippon Airways', 1, 50),
('All Nippon Airways', 2, 100),
('All Nippon Airways', 3, 200),
('American Airline', 1, 50),
('Eastern Airline', 1, 50),
('Southern Airline', 1, 50);

-- --------------------------------------------------------

--
-- 表的结构 `airport`
--

CREATE TABLE `airport` (
  `airport_name` varchar(50) NOT NULL,
  `airport_city` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `airport`
--

INSERT INTO `airport` (`airport_name`, `airport_city`) VALUES
('CTU', 'Cheng Du'),
('HKG', 'Hong Kong'),
('JFK', 'New York'),
('KIX', 'Osaka'),
('NRT', 'Tokyo'),
('PVG', 'Shanghai');

--
-- 触发器 `airport`
--
DELIMITER $$
CREATE TRIGGER `airport_format` BEFORE INSERT ON `airport` FOR EACH ROW BEGIN
IF (BINARY UPPER(new.airport_name) <> (BINARY new.airport_name)) or (BINARY UPPER(new.airport_city) = (BINARY new.airport_city)) THEN
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Airport should be all in uppercase and city should not be all in uppercase';
END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- 表的结构 `booking_agent`
--

CREATE TABLE `booking_agent` (
  `email` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `booking_agent_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `booking_agent`
--

INSERT INTO `booking_agent` (`email`, `password`, `booking_agent_id`) VALUES
('agent001@qq.com', 'b59c67bf196a4758191e42f76670ceba', 1),
('agent002@qq.com', 'b59c67bf196a4758191e42f76670ceba', 2),
('agent003@qq.com', 'b59c67bf196a4758191e42f76670ceba', 3),
('agent004@qq.com', 'b59c67bf196a4758191e42f76670ceba', 4),
('agent005@qq.com', 'b59c67bf196a4758191e42f76670ceba', 5),
('agent006@qq.com', 'b59c67bf196a4758191e42f76670ceba', 6),
('agent007@qq.com', 'b59c67bf196a4758191e42f76670ceba', 7),
('agent008@qq.com', 'b59c67bf196a4758191e42f76670ceba', 8);

--
-- 触发器 `booking_agent`
--
DELIMITER $$
CREATE TRIGGER `agent_format` BEFORE INSERT ON `booking_agent` FOR EACH ROW BEGIN
IF NOT (new.email LIKE '%@%') THEN
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Please enter valid email address';
END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- 替换视图以便查看 `commission`
-- （参见下面的实际视图）
--
CREATE TABLE `commission` (
`booking_agent_id` int(11)
,`total_commission` decimal(34,1)
,`num_of_tickets` bigint(21)
);

-- --------------------------------------------------------

--
-- 表的结构 `customer`
--

CREATE TABLE `customer` (
  `email` varchar(50) NOT NULL,
  `name` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `building_number` varchar(30) NOT NULL,
  `street` varchar(30) NOT NULL,
  `city` varchar(30) NOT NULL,
  `state` varchar(30) NOT NULL,
  `phone_number` char(11) NOT NULL,
  `passport_number` varchar(30) NOT NULL,
  `passport_expiration` date NOT NULL,
  `passport_country` varchar(50) NOT NULL,
  `date_of_birth` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `customer`
--

INSERT INTO `customer` (`email`, `name`, `password`, `building_number`, `street`, `city`, `state`, `phone_number`, `passport_number`, `passport_expiration`, `passport_country`, `date_of_birth`) VALUES
('customer001@qq.com', 'Gracie Zhou', 'b59c67bf196a4758191e42f76670ceba', '1555', 'Century Avenue', 'Shanghai', 'Shanghai', '1234567890', '1111', '2029-04-25', 'China', '1982-06-23'),
('customer002@qq.com', 'Melissa Xu', 'b59c67bf196a4758191e42f76670ceba', '1555', 'Century Avenue', 'Shanghai', 'Shanghai', '1234567890', '1111', '2029-04-25', 'China', '1999-06-23'),
('customer003@qq.com', 'Lily Wang', 'b59c67bf196a4758191e42f76670ceba', '1555', 'Century Avenue', 'Shanghai', 'Shanghai', '1234567890', '1111', '2029-04-25', 'China', '1999-06-23'),
('customer004@qq.com', 'Cat Chen', 'b59c67bf196a4758191e42f76670ceba', '1555', 'Century Avenue', 'Shanghai', 'Shanghai', '1234567890', '1111', '2029-04-25', 'China', '1999-06-23'),
('hl3797@nyu.edu', 'Hammond Liu', 'b59c67bf196a4758191e42f76670ceba', 'North 5th floor', 'West Yangsi Road 567', 'Shanghai', 'China', '666666', '777777', '2030-09-09', 'China', '2001-01-12'),
('qz1086@nyu.edu', 'Qianyu Zhu', 'b59c67bf196a4758191e42f76670ceba', '25', 'Union Square W', 'New York City', 'NY', '646409', 'SW1234', '2027-10-28', 'China', '2001-01-01');

--
-- 触发器 `customer`
--
DELIMITER $$
CREATE TRIGGER `customer_format` BEFORE INSERT ON `customer` FOR EACH ROW BEGIN
IF NOT (new.email LIKE '%@%') THEN
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Please enter a valid email address';
END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- 表的结构 `flight`
--

CREATE TABLE `flight` (
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL,
  `departure_airport` varchar(50) NOT NULL,
  `departure_time` datetime NOT NULL,
  `arrival_airport` varchar(50) NOT NULL,
  `arrival_time` datetime NOT NULL,
  `price` decimal(10,0) NOT NULL,
  `status` varchar(50) NOT NULL,
  `airplane_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `flight`
--

INSERT INTO `flight` (`airline_name`, `flight_num`, `departure_airport`, `departure_time`, `arrival_airport`, `arrival_time`, `price`, `status`, `airplane_id`) VALUES
('All Nippon Airways', 1, 'JFK', '2023-05-12 13:00:00', 'NRT', '2023-05-12 20:00:00', '7000', 'on time', 1),
('All Nippon Airways', 2, 'JFK', '2023-05-12 13:00:00', 'NRT', '2023-05-13 09:00:00', '10000', 'on time', 1),
('All Nippon Airways', 3, 'PVG', '2023-09-01 02:00:00', 'NRT', '2023-09-01 11:00:00', '10000', 'on time', 1),
('American Airline', 1, 'HKG', '2023-05-12 13:00:00', 'JFK', '2023-05-12 23:00:00', '5000', 'on time', 1),
('Eastern Airline', 1, 'PVG', '2023-04-29 13:20:00', 'NRT', '2023-04-29 15:20:00', '3000', 'on time', 1),
('Eastern Airline', 2, 'CTU', '2023-04-30 13:10:00', 'HKG', '2023-04-30 16:10:00', '1000', 'on time', 1),
('Southern Airline', 1, 'CTU', '2023-06-12 13:00:00', 'HKG', '2023-06-12 15:00:00', '1000', 'on time', 1);

--
-- 触发器 `flight`
--
DELIMITER $$
CREATE TRIGGER `time_conflict` BEFORE INSERT ON `flight` FOR EACH ROW BEGIN
IF NOT (new.departure_time < new.arrival_time) THEN
SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'CONFLICT TIME';
END IF;
END
$$
DELIMITER ;

-- --------------------------------------------------------

--
-- 表的结构 `permission`
--

CREATE TABLE `permission` (
  `username` varchar(50) NOT NULL,
  `permission_id` int(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `permission`
--

INSERT INTO `permission` (`username`, `permission_id`) VALUES
('Staff001', 3),
('Staff002', 1),
('Staff003', 3),
('Staff004', 1),
('Staff007', 2);

-- --------------------------------------------------------

--
-- 替换视图以便查看 `popular_dest`
-- （参见下面的实际视图）
--
CREATE TABLE `popular_dest` (
`airport_city` varchar(50)
,`num_flights` bigint(21)
);

-- --------------------------------------------------------

--
-- 表的结构 `purchases`
--

CREATE TABLE `purchases` (
  `ticket_id` int(11) NOT NULL,
  `customer_email` varchar(50) NOT NULL,
  `booking_agent_id` int(11) DEFAULT NULL,
  `purchase_date` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `purchases`
--

INSERT INTO `purchases` (`ticket_id`, `customer_email`, `booking_agent_id`, `purchase_date`) VALUES
(13578, 'customer001@qq.com', 1, '2023-02-12'),
(13579, 'customer003@qq.com', NULL, '2023-01-12'),
(24000, 'customer004@qq.com', 4, '2023-03-31'),
(24680, 'customer003@qq.com', 3, '2023-03-25'),
(24681, 'customer002@qq.com', NULL, '2023-04-01'),
(24682, 'customer001@qq.com', NULL, '2023-04-02'),
(24690, 'customer004@qq.com', NULL, '2023-04-06'),
(24691, 'customer003@qq.com', 3, '2022-12-17'),
(25000, 'customer001@qq.com', NULL, '2023-01-12'),
(25001, 'customer002@qq.com', 2, '2023-02-08'),
(25002, 'customer003@qq.com', 2, '2023-03-12'),
(192779660, 'qz1086@nyu.edu', NULL, '2023-04-12'),
(738143866, 'customer001@qq.com', 1, '2023-04-16'),
(738143867, 'customer001@qq.com', NULL, '2023-05-07'),
(738143868, 'customer001@qq.com', NULL, '2023-05-07'),
(738143869, 'customer001@qq.com', NULL, '2023-05-07'),
(738143870, 'customer001@qq.com', NULL, '2023-05-07'),
(738143871, 'customer001@qq.com', NULL, '2023-05-07'),
(738143872, 'customer001@qq.com', NULL, '2023-05-07'),
(738143873, 'hl3797@nyu.edu', 1, '2023-05-07'),
(738143874, 'hl3797@nyu.edu', 1, '2023-05-07');

-- --------------------------------------------------------

--
-- 表的结构 `ticket`
--

CREATE TABLE `ticket` (
  `ticket_id` int(11) NOT NULL,
  `airline_name` varchar(50) NOT NULL,
  `flight_num` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `ticket`
--

INSERT INTO `ticket` (`ticket_id`, `airline_name`, `flight_num`) VALUES
(13578, 'All Nippon Airways', 1),
(13579, 'All Nippon Airways', 1),
(738143866, 'All Nippon Airways', 1),
(738143867, 'All Nippon Airways', 1),
(738143868, 'All Nippon Airways', 1),
(738143869, 'All Nippon Airways', 1),
(738143870, 'All Nippon Airways', 1),
(738143871, 'All Nippon Airways', 1),
(738143872, 'All Nippon Airways', 1),
(25000, 'American Airline', 1),
(25001, 'American Airline', 1),
(25002, 'American Airline', 1),
(738143873, 'American Airline', 1),
(738143874, 'American Airline', 1),
(24680, 'Eastern Airline', 1),
(24681, 'Eastern Airline', 1),
(24682, 'Eastern Airline', 1),
(192779660, 'Eastern Airline', 1),
(24690, 'Eastern Airline', 2),
(24691, 'Eastern Airline', 2),
(24692, 'Eastern Airline', 2),
(24000, 'Southern Airline', 1),
(24001, 'Southern Airline', 1),
(24002, 'Southern Airline', 1);

-- --------------------------------------------------------

--
-- 替换视图以便查看 `top_customer`
-- （参见下面的实际视图）
--
CREATE TABLE `top_customer` (
`name` varchar(50)
,`customer_email` varchar(50)
,`phone_number` char(11)
,`passport_country` varchar(50)
,`total_flights` bigint(21)
);

-- --------------------------------------------------------

--
-- 表的结构 `works_for`
--

CREATE TABLE `works_for` (
  `email` varchar(50) NOT NULL,
  `airline_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

--
-- 转存表中的数据 `works_for`
--

INSERT INTO `works_for` (`email`, `airline_name`) VALUES
('agent001@qq.com', 'All Nippon Airways'),
('agent002@qq.com', 'American Airline'),
('agent003@qq.com', 'Eastern Airline'),
('agent004@qq.com', 'Southern Airline'),
('agent005@qq.com', 'All Nippon Airways'),
('agent006@qq.com', 'All Nippon Airways'),
('agent007@qq.com', 'American Airline');

-- --------------------------------------------------------

--
-- 视图结构 `commission`
--
DROP TABLE IF EXISTS `commission`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `air`.`commission`  AS   (select `air`.`purchases`.`booking_agent_id` AS `booking_agent_id`,sum(`air`.`flight`.`price` * 0.1) AS `total_commission`,count(0) AS `num_of_tickets` from ((`air`.`purchases` join `air`.`ticket` on(`air`.`purchases`.`ticket_id` = `air`.`ticket`.`ticket_id`)) join `air`.`flight` on(`air`.`ticket`.`airline_name` = `air`.`flight`.`airline_name` and `air`.`ticket`.`flight_num` = `air`.`flight`.`flight_num`)) where `air`.`purchases`.`purchase_date` between '2022-11-07 20:59:35.403249' and '2023-05-07 20:59:35.403249' group by `air`.`purchases`.`booking_agent_id` having `air`.`purchases`.`booking_agent_id` is not null)  ;

-- --------------------------------------------------------

--
-- 视图结构 `popular_dest`
--
DROP TABLE IF EXISTS `popular_dest`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `air`.`popular_dest`  AS   (select `P`.`airport_city` AS `airport_city`,count(0) AS `num_flights` from ((`air`.`airport` `P` join `air`.`flight` `F` on(`P`.`airport_name` = `F`.`arrival_airport`)) join `air`.`ticket` `T` on(`F`.`airline_name` = `T`.`airline_name` and `F`.`flight_num` = `T`.`flight_num`)) where `F`.`departure_time` between '0001-05-07 21:11:38.385500' and '2023-05-07 21:11:38.385500' group by `P`.`airport_city`)  ;

-- --------------------------------------------------------

--
-- 视图结构 `top_customer`
--
DROP TABLE IF EXISTS `top_customer`;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `air`.`top_customer`  AS   (select `air`.`customer`.`name` AS `name`,`air`.`purchases`.`customer_email` AS `customer_email`,`air`.`customer`.`phone_number` AS `phone_number`,`air`.`customer`.`passport_country` AS `passport_country`,count(0) AS `total_flights` from ((`air`.`purchases` join `air`.`ticket` on(`air`.`purchases`.`ticket_id` = `air`.`ticket`.`ticket_id`)) join `air`.`customer` on(`air`.`purchases`.`customer_email` = `air`.`customer`.`email`)) where `air`.`purchases`.`purchase_date` between '2022-05-07 21:03:43.484443' and '2023-05-07 21:03:43.484443' and `air`.`ticket`.`airline_name` = 'All Nippon Airways' group by `air`.`purchases`.`customer_email`)  ;

--
-- 转储表的索引
--

--
-- 表的索引 `airline`
--
ALTER TABLE `airline`
  ADD PRIMARY KEY (`airline_name`);

--
-- 表的索引 `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD PRIMARY KEY (`username`),
  ADD KEY `airline_name` (`airline_name`);

--
-- 表的索引 `airplane`
--
ALTER TABLE `airplane`
  ADD PRIMARY KEY (`airline_name`,`airplane_id`);

--
-- 表的索引 `airport`
--
ALTER TABLE `airport`
  ADD PRIMARY KEY (`airport_name`);

--
-- 表的索引 `booking_agent`
--
ALTER TABLE `booking_agent`
  ADD PRIMARY KEY (`email`);

--
-- 表的索引 `customer`
--
ALTER TABLE `customer`
  ADD PRIMARY KEY (`email`);

--
-- 表的索引 `flight`
--
ALTER TABLE `flight`
  ADD PRIMARY KEY (`airline_name`,`flight_num`),
  ADD KEY `airline_name` (`airline_name`,`airplane_id`),
  ADD KEY `departure_airport` (`departure_airport`),
  ADD KEY `arrival_airport` (`arrival_airport`);

--
-- 表的索引 `permission`
--
ALTER TABLE `permission`
  ADD PRIMARY KEY (`username`,`permission_id`);

--
-- 表的索引 `purchases`
--
ALTER TABLE `purchases`
  ADD PRIMARY KEY (`ticket_id`,`customer_email`),
  ADD KEY `customer_email` (`customer_email`),
  ADD KEY `purchase_date` (`purchase_date`);

--
-- 表的索引 `ticket`
--
ALTER TABLE `ticket`
  ADD PRIMARY KEY (`ticket_id`),
  ADD KEY `airline_name` (`airline_name`,`flight_num`);

--
-- 表的索引 `works_for`
--
ALTER TABLE `works_for`
  ADD PRIMARY KEY (`email`,`airline_name`),
  ADD KEY `airline_name` (`airline_name`);

--
-- 限制导出的表
--

--
-- 限制表 `airline_staff`
--
ALTER TABLE `airline_staff`
  ADD CONSTRAINT `airline_staff_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`);

--
-- 限制表 `airplane`
--
ALTER TABLE `airplane`
  ADD CONSTRAINT `airplane_ibfk_1` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`);

--
-- 限制表 `flight`
--
ALTER TABLE `flight`
  ADD CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`airline_name`,`airplane_id`) REFERENCES `airplane` (`airline_name`, `airplane_id`),
  ADD CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`departure_airport`) REFERENCES `airport` (`airport_name`),
  ADD CONSTRAINT `flight_ibfk_3` FOREIGN KEY (`arrival_airport`) REFERENCES `airport` (`airport_name`);

--
-- 限制表 `permission`
--
ALTER TABLE `permission`
  ADD CONSTRAINT `permission_ibfk_1` FOREIGN KEY (`username`) REFERENCES `airline_staff` (`username`);

--
-- 限制表 `purchases`
--
ALTER TABLE `purchases`
  ADD CONSTRAINT `purchases_ibfk_1` FOREIGN KEY (`ticket_id`) REFERENCES `ticket` (`ticket_id`),
  ADD CONSTRAINT `purchases_ibfk_2` FOREIGN KEY (`customer_email`) REFERENCES `customer` (`email`);

--
-- 限制表 `ticket`
--
ALTER TABLE `ticket`
  ADD CONSTRAINT `ticket_ibfk_1` FOREIGN KEY (`airline_name`,`flight_num`) REFERENCES `flight` (`airline_name`, `flight_num`);

--
-- 限制表 `works_for`
--
ALTER TABLE `works_for`
  ADD CONSTRAINT `works_for_ibfk_1` FOREIGN KEY (`email`) REFERENCES `booking_agent` (`email`),
  ADD CONSTRAINT `works_for_ibfk_2` FOREIGN KEY (`airline_name`) REFERENCES `airline` (`airline_name`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
