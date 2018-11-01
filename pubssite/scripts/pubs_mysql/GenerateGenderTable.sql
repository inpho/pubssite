USE `pubs`;

-- Procedure to update gender
DROP procedure IF EXISTS `Update_Gender`;

-- Create new procedure 'Update_Gender'
-- The purpose of Update_Gender is to automatically update the genders of authors in the db
-- Pt. 1: Add a temporary first name column
-- Pt. 2: Populate the Gender table based on unambiguous genders in the authors table
-- Pt. 3: Update the authors entries' genders based on gender table
-- Pt. 4: Remove the temporary first name column
DELIMITER $$
USE `pubs`$$
CREATE PROCEDURE `Update_Gender`()
BEGIN
	-- Pt. 1: Add first name column
	-- Add a fn (first name) column
	IF NOT EXISTS(SELECT NULL
            FROM INFORMATION_SCHEMA.COLUMNS
           WHERE table_name = 'authors'
             AND table_schema = 'pubs'
             AND column_name = 'fn') THEN
	ALTER TABLE pubs.authors
	ADD fn VARCHAR(50);
	END IF;
    
    -- Parse out first name from the firstname column (for first name columns that include middle names)
    UPDATE pubs.authors
	SET 
		fn = SUBSTRING(firstname, 1, LOCATE(' ', firstname)-1)
	WHERE LOCATE(' ', firstname)>0
    AND NOT LOCATE('.', SUBSTRING(firstname, 1, LOCATE(' ', firstname)))>0;
    
    -- For names that don't have middle names, set fn = firstname
    UPDATE pubs.authors
	SET 
		fn = firstname
	WHERE NOT LOCATE(' ', firstname)>0
    AND NOT LOCATE('.', SUBSTRING(firstname, 1, LOCATE(' ', firstname)))>0;
    
    -- Pt. 2: Populate Gender Table
    -- Take every name in author and add it to gender
	-- For every author name
	-- If it isn't in gender, add it with this author's gender
    
    -- For 'simple' given names (single word)
	INSERT IGNORE INTO gender (firstname, gender)
	SELECT authors.fn, authors.gender 
	FROM authors 
	WHERE authors.fn
	not in (SELECT gender.firstname FROM gender)
	AND CHAR_LENGTH(authors.gender) > 0
    AND NOT LOCATE(' ', authors.fn)>0;
    
    -- If it is in gender and the gender contradicts, make ambiguous
    UPDATE pubs.gender
	SET gender.gender = 'A'
	WHERE gender.firstname in 
	(SELECT * FROM
		(SELECT gender.firstname 
		FROM pubs.gender, pubs.authors
		WHERE gender.firstname = authors.fn
		AND NOT gender.gender = authors.gender
		AND NOT CHAR_LENGTH(authors.gender) = 0)
		as x
	);
    
    -- Pt. 3: Update Authors' Genders
    -- Update Authors' genders when they have first names we find gender-non-ambiguous
    
    -- Update authors we believe are male
    UPDATE pubs.authors
	SET authors.gender = 'M'
	WHERE authors.fn in 
	(SELECT gender.firstname
	FROM pubs.gender
	WHERE gender.gender = 'M'
	)
	AND CHAR_LENGTH(authors.gender) = 0;

	-- Update authors we believe are female
	UPDATE pubs.authors
	SET authors.gender = 'F'
	WHERE authors.fn in 
	(SELECT gender.firstname
	FROM pubs.gender
	WHERE gender.gender = 'F'
	)
	AND CHAR_LENGTH(authors.gender) = 0;
    
    -- Pt. 4: Drop the fn column
    ALTER TABLE authors DROP COLUMN fn;
END$$
DELIMITER ;
-- End procedure

-- Call update gender procedure
-- SET SQL_SAFE_UPDATES = 0;
-- CALL `pubs`.`Update_Gender`();

-- View contents of gender and author tables (Checking our work)
-- SELECT * FROM gender;
-- SELECT * FROM authors;