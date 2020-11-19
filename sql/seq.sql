DROP TABLE IF EXISTS sequences;


-- CREATE TABLE sequences (sequence_name VARCHAR(50),currval INT);
-- INSERT INTO sequences (sequence_name,currval) VALUES ('raw_sections',0); 


delimiter /
DROP TRIGGER section_sequence/
-- CREATE TRIGGER section_sequence
-- BEFORE INSERT ON raw_section FOR EACH ROW BEGIN
-- UPDATE sequences set currval = currval + 1 where sequence_name = 'raw_sections';
-- SET NEW.section_number = (SELECT currval FROM sequences WHERE sequence_name = 'raw_sections');
-- END;/
