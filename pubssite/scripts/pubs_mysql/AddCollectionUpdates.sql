CREATE TABLE IF NOT EXISTS `pubs`.`collections_update` (
  `fk_collections_id` INT NOT NULL,
  `publish_date` DATETIME NULL,
  `revision_date` DATETIME NULL,
  `update_date` DATETIME NULL,
  PRIMARY KEY (`fk_collections_id`),
  INDEX `fk_collections_collection1_idx` (`fk_collections_id` ASC),
  CONSTRAINT `fk_collections_collection1`
    FOREIGN KEY (`fk_collections_id`)
    REFERENCES `pubs`.`collections` (`collection_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

INSERT IGNORE INTO pubs.collections_update (fk_collections_id)
	SELECT collection_id
	FROM pubs.collections 
	WHERE collection_id NOT IN 
    (SELECT fk_collections_id FROM pubs.collections_update);