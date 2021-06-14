drop table if exists com_type;
CREATE TABLE `com_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `input_type` varchar(50) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT 1,
  `created` datetime(6) NOT NULL,
  `updated` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `K__CT_INID` (`input_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
insert into com_type (input_type, active, created, updated) values ('manual', 1 ,NOW(), NOW());
insert into com_type (input_type, active, created, updated) values ('corrected', 1 ,NOW(), NOW());
insert into com_type (input_type, active, created, updated) values ('detected', 1 ,NOW(), NOW());
insert into com_type (input_type, active, created, updated) values ('aligned', 1 ,NOW(), NOW());
-- transformation
ALTER TABLE transformation ADD COLUMN input_type_id INT(11) NOT NULL DEFAULT 1 AFTER person_id;
UPDATE transformation SET input_type_id = 1;
ALTER TABLE transformation ADD INDEX K__T_ITID (input_type_id);
ALTER TABLE transformation ADD CONSTRAINT FK__T_ITID FOREIGN KEY (input_type_id) REFERENCES com_type(id);
ALTER TABLE transformation DROP INDEX K__T_INID;
ALTER TABLE transformation DROP INDEX UK__T_AID_PID_INID;
ALTER TABLE transformation DROP COLUMN input_type;
ALTER TABLE transformation ADD CONSTRAINT `UK__T_AID_PID_ITID` UNIQUE (prep_id, person_id, input_type_id);
-- center_of_mass
ALTER TABLE center_of_mass ADD COLUMN input_type_id INT(11) NOT NULL DEFAULT 1 AFTER person_id;
UPDATE center_of_mass SET input_type_id = 1 where input_type='manual';
UPDATE center_of_mass SET input_type_id = 3 where input_type='detected';
UPDATE center_of_mass SET input_type_id = 4 where input_type='aligned';
ALTER TABLE center_of_mass ADD INDEX K__COM_ITID (input_type_id);
ALTER TABLE center_of_mass ADD CONSTRAINT FK__COM_ITID FOREIGN KEY (input_type_id) REFERENCES com_type(id);
ALTER TABLE center_of_mass DROP COLUMN input_type;

insert into center_of_mass (prep_id, structure_id, person_id, input_type_id,x,y,section,active,created,updated)
select prep_id, structure_id, person_id, 2 as input_type_id, x, y, section, 1, now(), now() 
from center_of_mass where prep_id  = 'DK52' and person_id=2 and input_type_id=1 and active=1 order by structure_id;

insert into center_of_mass (prep_id, structure_id, person_id, input_type_id,x,y,section,active,created,updated)
select prep_id, structure_id, person_id, 2 as input_type_id, x, y, section, 1, now(), now() 
from center_of_mass where prep_id  = 'DK54' and person_id=2 and input_type_id=1 and active=1 order by structure_id;

insert into center_of_mass (prep_id, structure_id, person_id, input_type_id,x,y,section,active,created,updated)
select prep_id, structure_id, person_id, 2 as input_type_id, x, y, section, 1, now(), now() 
from center_of_mass where prep_id  = 'DK39' and person_id=2 and input_type_id=1 and active=1 order by structure_id;

insert into center_of_mass (prep_id, structure_id, person_id, input_type_id,x,y,section,active,created,updated)
select prep_id, structure_id, person_id, 2 as input_type_id, x, y, section, 1, now(), now() 
from center_of_mass where prep_id  = 'DK43' and person_id=2 and input_type_id=1 and active=1 order by structure_id;

insert into center_of_mass (prep_id, structure_id, person_id, input_type_id,x,y,section,active,created,updated)
select prep_id, structure_id, person_id, 2 as input_type_id, x, y, section, 1, now(), now() 
from center_of_mass where prep_id  = 'DK41' and person_id=2 and input_type_id=1 and active=1 order by structure_id;
-- update with bili data
-- DK52
update center_of_mass set x = 38952	, y=18933, section=310	 where structure_id=9 and input_type_id=2 and person_id=2 and prep_id='DK52' and active=1;
update center_of_mass set x = 40603	, y=19210, section=257	 where structure_id=11 and input_type_id=2 and person_id=2 and prep_id='DK52' and active=1;
update center_of_mass set x = 40525	, y=19502, section=220	 where structure_id=10 and input_type_id=2 and person_id=2 and prep_id='DK52' and active=1;
update center_of_mass set x = 41930	, y=23268, section=178	 where structure_id=12 and input_type_id=2 and person_id=2 and prep_id='DK52' and active=1;
update center_of_mass set x = 41684	, y=17662, section=125	 where structure_id=19 and input_type_id=2 and person_id=2 and prep_id='DK52' and active=1;
update center_of_mass set x = 41783	, y=16420, section=351	 where structure_id=20 and input_type_id=2 and person_id=2 and prep_id='DK52' and active=1;
-- DK54
update center_of_mass set x = 29528	, y=15967, section=225	 where structure_id=4 and input_type_id=2 and person_id=2 and prep_id='DK54' and active=1;
update center_of_mass set x = 29557	, y=16107, section=242	 where structure_id=5 and input_type_id=2 and person_id=2 and prep_id='DK54' and active=1;
update center_of_mass set x = 37307	, y=22769, section=147	 where structure_id=12 and input_type_id=2 and person_id=2 and prep_id='DK54' and active=1;
update center_of_mass set x = 38451	, y=23224, section=280	 where structure_id=13 and input_type_id=2 and person_id=2 and prep_id='DK54' and active=1;
update center_of_mass set x = 34612	, y=18964, section=144	 where structure_id=8 and input_type_id=2 and person_id=2 and prep_id='DK54' and active=1;
-- DK39
update center_of_mass set x = 38561	, y=19734, section=235	 where structure_id=10 and input_type_id=2 and person_id=2 and prep_id='DK39' and active=1;
update center_of_mass set x = 40112	, y=18516, section=135	 where structure_id=19 and input_type_id=2 and person_id=2 and prep_id='DK39' and active=1;
insert into center_of_mass(prep_id, structure_id, person_id, input_type_id,x,y,section,active,created,updated) 
values ('DK39',20,2,2,38270,16977,373,1,NOW(),NOW());
-- DK43
-- update center_of_mass set x = 39091	, y=754	, section=242	 where structure_id=11 and input_type_id=2 and person_id=2 and prep_id='DK43' and active=1;
insert into center_of_mass(prep_id, structure_id, person_id, input_type_id,x,y,section,active,created,updated) 
values ('DK43',11,2,2,39091,754,242,1,NOW(),NOW());


update center_of_mass set x = 36994, y=22941, section=150	 where structure_id=12 and input_type_id=2 and person_id=2 and prep_id='DK43' and active=1;
-- DK41
update center_of_mass set x = 38309, y=	23734, section=163	 where structure_id=12 and input_type_id=2 and person_id=2 and prep_id='DK41' and active=1;

