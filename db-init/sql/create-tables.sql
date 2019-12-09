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
CREATE TABLE IF NOT EXISTS `#MYSQL_DB#`.`ecotypes` (
	  `id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	  `name` VARCHAR(191) NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE)
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`contigs`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `#MYSQL_DB#`.`contigs` (
	  `id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	  `name` VARCHAR(191) NOT NULL,
	  `ecotype_id` SMALLINT UNSIGNED NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `contigs_name_UNIQUE` (`name` ASC) VISIBLE)
	  INDEX `contigs_ecotypes_fk_idx` (`ecotype_id` ASC) VISIBLE,
	  CONSTRAINT `contigs_ecotypes_fk`
	    FOREIGN KEY (`ecotype_id`)
	    REFERENCES `#MYSQL_DB#`.`ecotypes` (`id`)
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`genes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `#MYSQL_DB#`.`genes` (
	  `gene_id` MEDIUMINT UNSIGNED NOT NULL AUTO_INCREMENT,
	  `length` SMALLINT UNSIGNED NOT NULL,
	  `ecotype_id` SMALLINT UNSIGNED NOT NULL,
	  PRIMARY KEY (`gene_id`),
	  INDEX `genes_ecotypes_fk_idx` (`ecotype_id` ASC) VISIBLE,
	  CONSTRAINT `genes_ecotypes_fk`
            FOREIGN KEY (`ecotype_id`)
	    REFERENCES `#MYSQL_DB#`.`ecotypes` (`id`)
	)
	ENGINE = InnoDB
	DEFAULT CHAR SET = utf8mb4
	COLLATE=utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `#MYSQL_DB#`.`stations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `#MYSQL_DB#`.`stations` (
	  `id` SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
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
	  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
	  `contig_id` SMALLINT UNSIGNED NOT NULL,
	  `gene_id` MEDIUMINT UNSIGNED NOT NULL,
	  `station_id` SMALLINT UNSIGNED NOT NULL,
	  `read_number` INT UNSIGNED NOT NULL,
	  `read_length` INT UNSIGNED NOT NULL,
	  `gc_content` DECIMAL(4,2) NOT NULL,
	  PRIMARY KEY (`id`),
	  UNIQUE INDEX `gene_reads_gene_read_station_unique` (`gene_id` ASC, `read_number` ASC, `station_id` ASC) VISIBLE,
	  INDEX `gene_reads_stations_fk_idx` (`station_id` ASC) VISIBLE,
	  INDEX `gene_reads_contigs_fk_idx` (`contig_id` ASC) VISIBLE,
	  INDEX `gene_reads_genes_fk_idx` (`gene_id` ASC) VISIBLE,
	  CONSTRAINT `gene_reads_contigs_fk`
            FOREIGN KEY (`contig_id`)
	    REFERENCES `#MYSQL_DB#`.`contigs` (`id`),
	  CONSTRAINT `gene_reads_stations_fk`
            FOREIGN KEY (`station_id`)
	    REFERENCES `#MYSQL_DB#`.`stations` (`id`),
	  CONSTRAINT `gene_reads_genes_fk`
            FOREIGN KEY (`gene_id`)
	    REFERENCES `#MYSQL_DB#`.`genes` (`gene_id`)
        )
	ENGINE = InnoDB
	DEFAULT CHARACTER SET = utf8mb4
	COLLATE = utf8mb4_0900_ai_ci;

-- -----------------------------------------------------

	SET SQL_MODE=@OLD_SQL_MODE;
	SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
	SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
