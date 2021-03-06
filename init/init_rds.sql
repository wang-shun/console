INSERT INTO `rds_db_version` VALUES
('1', '2016-11-09 04:12:11.147000', '2016-11-09 04:12:11.147000', '2016-11-09 04:12:11.147000', '0', 'rdbv-00000001', 'mysql', '5.6'),
('2', '2016-11-09 04:12:11.147000', '2016-11-09 04:12:11.147000', '2016-11-09 04:12:11.147000', '0', 'rdbv-00000002', 'oracle', '11g');

INSERT INTO `rds_flavor` VALUES
(1,'2016-05-24 00:00:00','2016-05-24 00:00:00',NULL,0,'c1m1d20','1核1G',1,1,'1核1G','0'),
(2,'2016-06-08 00:00:00','2016-06-08 00:00:00',NULL,0,'c1m2d20','1核2G',1,2,'1核2G','16'),
(3,'2016-06-08 00:00:00','2016-06-08 00:00:00',NULL,0,'c2m4d20','2核4G',2,4,'2核4G','304'),
(4,'2016-06-08 00:00:00','2016-06-08 00:00:00',NULL,0,'c2m8d20','2核8G',2,8,'2核8G','368'),
(5,'2016-06-08 00:00:00','2016-06-08 00:00:00',NULL,0,'c4m8d20','4核8G',4,8,'4核8G','880'),
(6,'2016-06-08 00:00:00','2016-06-08 00:00:00',NULL,0,'c4m16d20','4核16G',4,16,'4核16G','1008'),
(7,'2016-06-08 00:00:00','2016-06-08 00:00:00',NULL,0,'c8m16d20','8核16G',8,16,'8核16G','2032'),
(8,'2016-06-08 00:00:00','2016-06-08 00:00:00',NULL,0,'c8m32d20','8核32G',8,32,'8核32G','2288'),
(9,'2016-06-08 00:00:00','2016-06-08 00:00:00',NULL,0,'c16m64d20','16核64G',16,64,'16核64G','4848');

INSERT INTO `rds_iops` VALUES
(1,'lvm_sata',300,1),(2,'lvm_sata',300,2),(3,'lvm_sata',500,3),
(4,'lvm_sata',500,4),(5,'lvm_sata',1000,5),(6,'lvm_sata',1000,6),
(7,'lvm_sata',2000,7),(8,'lvm_sata',2000,8),(9,'lvm_sata',2000,9),
(10,'lvm_ssd',600,1),(11,'lvm_ssd',1000,2),(12,'lvm_ssd',2000,3),
(13,'lvm_ssd',2000,4),(14,'lvm_ssd',5000,5),(15,'lvm_ssd',7000,6),
(16,'lvm_ssd',8000,7),(17,'lvm_ssd',12000,8),(18,'lvm_ssd',14000,9),
(19,'lvm_pcie',1000,1),(20,'lvm_pcie',2000,2),(21,'lvm_pcie',4000,3),
(22,'lvm_pcie',4000,4),(23,'lvm_pcie',8000,5),(24,'lvm_pcie',10000,6),
(25,'lvm_pcie',14000,7),(26,'lvm_pcie',16000,8),(27,'lvm_pcie',20000,9),
(28,'sata',300,1),(29,'sata',300,2),(30,'sata',500,3),(31,'sata',500,4),
(32,'sata',1000,5),(33,'sata',1000,6),(34,'sata',2000,7),(35,'sata',2000,8),
(36,'sata',2000,9),(37,'ssd',600,1),(38,'ssd',1000,2),(39,'ssd',2000,3),
(40,'ssd',2000,4),(41,'ssd',5000,5),(42,'ssd',7000,6),(43,'ssd',8000,7),
(44,'ssd',12000,8),(45,'ssd',14000,9),(46,'pcie',1000,1),(47,'pcie',2000,2),
(48,'pcie',4000,3),(49,'pcie',4000,4),(50,'pcie',8000,5),(51,'pcie',10000,6),
(52,'pcie',14000,7),(53,'pcie',16000,8),(54,'pcie',20000,9);
