-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema #MYSQL_DB#
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema #MYSQL_DB#
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `#MYSQL_DB#` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `#MYSQL_DB#` ;

-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`ecotypes`
-- -----------------------------------------------------
CREATE TABLE `rarefaction_I09`.`ecotypes` (
	  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	  `name` VARCHAR(191) NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE);
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`contigs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `#MYSQL_DB#`.`contigs` (
	  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	  `name` VARCHAR(191) NULL DEFAULT NULL,
	  `ecotype_id` INT(11) UNSIGNED,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`stations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `#MYSQL_DB#`.`stations` (
	  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	  `name` VARCHAR(12) NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`gene_reads`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `#MYSQL_DB#`.`gene_reads` (
	  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	  `gene_id` INT(10) UNSIGNED NOT NULL,
	  `read_number` INT(10) UNSIGNED NOT NULL,
	  `station_id` INT(10) UNSIGNED NOT NULL,
	  `contig_id` INT(10) UNSIGNED NOT NULL,
	  `read_length` INT(10) UNSIGNED NOT NULL,
	  `gc_content` DECIMAL(4,2) UNSIGNED NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `gene_read_station_unique` (`gene_id` ASC, `read_number` ASC, `station_id` ASC) VISIBLE,
	  INDEX `station_fk_idx` (`station_id` ASC) VISIBLE,
	  INDEX `contig_fk_idx` (`contig_id` ASC) VISIBLE,
	  CONSTRAINT `contig_fk`
	    FOREIGN KEY (`contig_id`)
	    REFERENCES `#MYSQL_DB#`.`contigs` (`id`),
	  CONSTRAINT `station_fk`
	    FOREIGN KEY (`station_id`)
	    REFERENCES `#MYSQL_DB#`.`stations` (`id`))
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


	SET SQL_MODE=@OLD_SQL_MODE;
	SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
	SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`gene_reads`
-- -----------------------------------------------------
CREATE TABLE `gene_ref_lengths` (
	  `gene_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
	  `length` smallint(5) unsigned NOT NULL,
	  PRIMARY KEY (`gene_id`),
	  UNIQUE KEY `gene_id_UNIQUE` (`gene_id`)
	)
	ENGINE = InnoDB
	DEFAULT CHAR SET = utf8mb4
	COLLATE=utf8mb4_0900_ai_ci;
