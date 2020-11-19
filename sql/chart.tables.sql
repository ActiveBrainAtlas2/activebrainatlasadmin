-- drops
DROP TABLE IF EXISTS `chart_task_resources`;
DROP TABLE IF EXISTS `chart_task`;
DROP TABLE IF EXISTS `chart_schedule`;
DROP TABLE IF EXISTS `chart_resource`;
DROP TABLE IF EXISTS `chart_roles`;

--
-- Table structure for table `chart_schedule`
--

CREATE TABLE `chart_schedule` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) DEFAULT NULL,
  `description` longtext,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `duration` int(11) NOT NULL,
  `start_date` datetime(6) DEFAULT NULL,
  `end_date` datetime(6) DEFAULT NULL,
  `can_write` tinyint(1) NOT NULL,
  `can_write_on_parent` tinyint(1) NOT NULL,
  `selected_row` int(11) NOT NULL,
  `prep_id` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `K__CHART_SCHEDULE_prep_id` (`prep_id`),
  CONSTRAINT `FK__CHART_SCHEDULE_prep_id` FOREIGN KEY (`prep_id`) REFERENCES `animal` (`prep_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


--
-- Table structure for table `chart_task`
--

CREATE TABLE `chart_task` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(250) DEFAULT NULL,
  `description` longtext,
  `created` datetime(6) NOT NULL,
  `updated` datetime(6) NOT NULL,
  `duration` int(11) NOT NULL,
  `start_date` datetime(6) DEFAULT NULL,
  `end_date` datetime(6) DEFAULT NULL,
  `level` int(11) NOT NULL,
  `is_milestone` tinyint(1) NOT NULL,
  `end_is_milestone` tinyint(1) NOT NULL,
  `status` varchar(300) DEFAULT NULL,
  `progress` decimal(10,2) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `schedule_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `K__CHART_TASK_task_id` (`parent_id`),
  KEY `K__CHART_TASK_schedule_id` (`schedule_id`),
  CONSTRAINT `FK__CHART_TASK__schedule_id` FOREIGN KEY (`schedule_id`) REFERENCES `chart_schedule` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Table structure for table `chart_roles`
--

CREATE TABLE `chart_roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


--
-- Table structure for table `chart_resource`
--

CREATE TABLE `chart_resource` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `effort` int(11) NOT NULL,
  `role_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `K__CHART_RESOURCE_role_id` (`role_id`),
  CONSTRAINT `FK__CHART_RESOURCE_roles_id` FOREIGN KEY (`role_id`) REFERENCES `chart_roles` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;


--
-- Table structure for table `chart_task_resources`
--

CREATE TABLE `chart_task_resources` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `task_id` int(11) NOT NULL,
  `resource_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UK__CHART_TASK_RESOURCE_task_id` (`task_id`,`resource_id`),
  KEY `K__CHART_TASK_RESOURCE_resource_id` (`resource_id`),
  CONSTRAINT `FK__CHART_TASK_RESOURCE_resource_id` FOREIGN KEY (`resource_id`) REFERENCES `chart_resource` (`id`),
  CONSTRAINT `FK__CHART_TASK_RESOURCE_task_id` FOREIGN KEY (`task_id`) REFERENCES `chart_task` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

