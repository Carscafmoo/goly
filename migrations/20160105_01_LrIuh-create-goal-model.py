"""
Create goal model
"""

from yoyo import step

__depends__ = {}

steps = [
    step("""CREATE TABLE `frequency` 
      (`id` SMALLINT UNSIGNED AUTO_INCREMENT, `name` VARCHAR(31) NOT NULL, `rule` VARCHAR(255),
        PRIMARY KEY(`id`),
        UNIQUE KEY(`name`))""", 
      "DROP TABLE IF EXISTS `frequency`"),
    step("""CREATE TABLE `input_type` (`id` SMALLINT UNSIGNED AUTO_INCREMENT, `name` VARCHAR(31) NOT NULL,
      PRIMARY KEY(`id`), UNIQUE KEY(`name`))""",
      "DROP TABLE IF EXISTS `input_type`"),
    step("""CREATE TABLE `goal`
      (`id` BIGINT UNSIGNED AUTO_INCREMENT, 
        `name` VARCHAR(63) NOT NULL COMMENT 'A short descriptor of the goal, used for tracking', 
        `prompt` VARCHAR(255) NOT NULL COMMENT 'A long descriptor of the goal, in format similar to "Did you do X today"', 
        `input_type` SMALLINT UNSIGNED NOT NULL COMMENT 'The type of input that the prompt will receive (e.g., "yes/no")',
        `target` INT NOT NULL COMMENT 'A numeric target for the goal, e.g., 2 (times per year) or 160 (lbs by Feb. 28)"',
        `frequency` SMALLINT UNSIGNED DEFAULT NULL COMMENT 'The frequency with which to complete the goal, e.g., (2) times per week',
        `date` DATE DEFAULT NULL COMMENT 'The date by which to complete the goal, e.g. (160 lbs by) Feb 28',
        PRIMARY KEY(`id`),
        FOREIGN KEY (`frequency`) REFERENCES `frequency` (`id`) ON UPDATE CASCADE,
        FOREIGN KEY (`input_type`) REFERENCES `input_type` (`id`) ON UPDATE CASCADE)""",
        "DROP TABLE IF EXISTS `goal`"
      )


]
