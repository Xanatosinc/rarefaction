-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema rarefaction
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema rarefaction
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `rarefaction` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `rarefaction` ;

-- -----------------------------------------------------
-- Table `rarefaction`.`contigs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rarefaction`.`contigs` (
	  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
	  `name` VARCHAR(45) NULL DEFAULT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


	-- -----------------------------------------------------
-- Table `rarefaction`.`stations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rarefaction`.`stations` (
	  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
	  `name` VARCHAR(6) NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


	-- -----------------------------------------------------
-- Table `rarefaction`.`gene_reads`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `rarefaction`.`gene_reads` (
	  `id` INT(10) UNSIGNED NOT NULL,
	  `gene_id` INT(10) UNSIGNED NOT NULL,
	  `read_number` INT(10) UNSIGNED NOT NULL,
	  `station_id` INT(10) UNSIGNED NOT NULL,
	  `contig_id` INT(10) UNSIGNED NOT NULL,
	  `read_length` INT(10) UNSIGNED NOT NULL,
	  `gc_content` DECIMAL(4,2) UNSIGNED NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `gene_read_unique` (`gene_id` ASC, `read_number` ASC) VISIBLE,
	  INDEX `station_fk_idx` (`station_id` ASC) VISIBLE,
	  INDEX `contig_fk_idx` (`contig_id` ASC) VISIBLE,
	  CONSTRAINT `contig_fk`
	    FOREIGN KEY (`contig_id`)
	    REFERENCES `rarefaction`.`contigs` (`id`),
	  CONSTRAINT `station_fk`
	    FOREIGN KEY (`station_id`)
	    REFERENCES `rarefaction`.`stations` (`id`))
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


	SET SQL_MODE=@OLD_SQL_MODE;
	SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
	SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

