-- phpMyAdmin SQL Dump
-- version 3.3.9
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Nov 18, 2012 at 01:58 PM
-- Server version: 5.5.8
-- PHP Version: 5.3.5

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `os_minor`
--

-- --------------------------------------------------------

--
-- Table structure for table `files`
--

CREATE TABLE IF NOT EXISTS `files` (
  `projectid` varchar(20) NOT NULL DEFAULT '',
  `filename` varchar(50) NOT NULL DEFAULT '',
  `modified_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `modified_by` varchar(20) NOT NULL DEFAULT '',
  `versions` int(50) NOT NULL,
  `hide` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`projectid`,`filename`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `files`
--

INSERT INTO `files` (`projectid`, `filename`, `modified_time`, `modified_by`, `versions`, `hide`) VALUES
('2', ' file99', '2012-11-14 18:17:02', 'miths1108', 1, 0),
('2', 'file', '2012-11-18 12:00:47', 'miths1108', 3, 0),
('2', 'file9', '2012-11-18 15:36:36', 'miths1108', 1, 0),
('2', 'newnew1', '2012-11-15 12:46:51', 'swe1807', 1, 0),
('2', 'newnew2', '2012-11-15 12:46:46', 'miths1108', 1, 0),
('2', 'original', '2012-11-16 19:41:36', 'miths1108', 2, 0),
('2', 'ren', '2012-11-14 18:36:34', 'miths1108', 1, 0),
('2', 'renamed file', '2012-11-14 18:37:02', 'swe1807', 1, 0),
('2', 'Untitled Document 1', '2012-11-16 19:15:22', 'miths1108', 3, 0);

-- --------------------------------------------------------

--
-- Table structure for table `members`
--

CREATE TABLE IF NOT EXISTS `members` (
  `username` varchar(50) NOT NULL DEFAULT '',
  `projectid` varchar(50) NOT NULL DEFAULT '',
  PRIMARY KEY (`projectid`,`username`),
  KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `members`
--

INSERT INTO `members` (`username`, `projectid`) VALUES
('miths1108', '1'),
('miths1108', '2'),
('swe1807', '2');

-- --------------------------------------------------------

--
-- Table structure for table `project_info`
--

CREATE TABLE IF NOT EXISTS `project_info` (
  `projectid` varchar(50) NOT NULL DEFAULT '',
  `projectname` varchar(100) NOT NULL,
  PRIMARY KEY (`projectid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `project_info`
--

INSERT INTO `project_info` (`projectid`, `projectname`) VALUES
('1', ''),
('2', 'repo1');

-- --------------------------------------------------------

--
-- Table structure for table `updations`
--

CREATE TABLE IF NOT EXISTS `updations` (
  `filename` varchar(50) NOT NULL DEFAULT '',
  `operation` varchar(10) NOT NULL DEFAULT '',
  `username` varchar(15) NOT NULL DEFAULT '',
  `operation_id` int(11) NOT NULL AUTO_INCREMENT,
  `filename_old` varchar(50) NOT NULL DEFAULT '',
  `version` int(11) DEFAULT '0',
  PRIMARY KEY (`operation_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=10 ;

--
-- Dumping data for table `updations`
--


-- --------------------------------------------------------

--
-- Table structure for table `user_info`
--

CREATE TABLE IF NOT EXISTS `user_info` (
  `username` varchar(50) NOT NULL DEFAULT '',
  `name` varchar(50) NOT NULL,
  `password` varchar(30) NOT NULL,
  `pc-name` varchar(20) NOT NULL,
  PRIMARY KEY (`username`,`pc-name`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Dumping data for table `user_info`
--

INSERT INTO `user_info` (`username`, `name`, `password`, `pc-name`) VALUES
('divya', 'divya', 'divya', 'divya-pc'),
('miths1108', 'Anupam Sanghi', 'miths1108', 'anupam-pc'),
('newcastle', 'pradeep', 'pradeep', 'pradeep-pc'),
('swe1807', 'sweksha', 'swe1807', 'sweksha-pc'),
('test', 'test', 'Test123', 'anupam-pc');

--
-- Constraints for dumped tables
--

--
-- Constraints for table `files`
--
ALTER TABLE `files`
  ADD CONSTRAINT `files_ibfk_1` FOREIGN KEY (`projectid`) REFERENCES `project_info` (`projectid`);

--
-- Constraints for table `members`
--
ALTER TABLE `members`
  ADD CONSTRAINT `members_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user_info` (`username`),
  ADD CONSTRAINT `members_ibfk_2` FOREIGN KEY (`projectid`) REFERENCES `project_info` (`projectid`);
