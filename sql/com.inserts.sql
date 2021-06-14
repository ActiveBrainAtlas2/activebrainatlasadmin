
-- 28 is ID for bili
-- repeat each insert statement below for each COM, make sure you end each statement with a ;
-- substitute 1111 for x, 222 for y and 333 for section (z), 1 is the structure_id, you need to look it up!
-- mysql active_atlas_production -e "select id from structure where abbreviation = '10N_L';"

insert into center_of_mass (prep_id,x,y,section,structure_id,person_id,created) values ('DK52',1111, 222, 333, 1, 28,NOW());
