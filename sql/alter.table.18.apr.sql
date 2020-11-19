update slide set 
insert_before_one=0,
insert_between_one_two=0,
insert_between_two_three=0,
insert_between_three_four=0,
insert_between_four_five=0,
insert_between_five_six=0 
where scan_run_id = 1;



-- OUTOFFOCUS = 1
-- BADTISSUE = 2
-- END = 3


alter table slide modify column scene_qc_1 enum('Out-of-Focus','Bad tissue','End','1','0','2','3');
alter table slide modify column scene_qc_2 enum('Out-of-Focus','Bad tissue','End','1','0','2','3');
alter table slide modify column scene_qc_3 enum('Out-of-Focus','Bad tissue','End','1','0','2','3');
alter table slide modify column scene_qc_4 enum('Out-of-Focus','Bad tissue','End','1','0','2','3');
alter table slide modify column scene_qc_5 enum('Out-of-Focus','Bad tissue','End','1','0','2','3');
alter table slide modify column scene_qc_6 enum('Out-of-Focus','Bad tissue','End','1','0','2','3');

update slide set scene_qc_1 = '1' where scene_qc_1 = 'Out-of-Focus';
update slide set scene_qc_2 = '1' where scene_qc_2 = 'Out-of-Focus';
update slide set scene_qc_3 = '1' where scene_qc_3 = 'Out-of-Focus';
update slide set scene_qc_4 = '1' where scene_qc_4 = 'Out-of-Focus';
update slide set scene_qc_5 = '1' where scene_qc_5 = 'Out-of-Focus';
update slide set scene_qc_6 = '1' where scene_qc_6 = 'Out-of-Focus';


update slide set scene_qc_1 = '2' where scene_qc_1 = 'Bad tissue';
update slide set scene_qc_2 = '2' where scene_qc_2 = 'Bad tissue';
update slide set scene_qc_3 = '2' where scene_qc_3 = 'Bad tissue';
update slide set scene_qc_4 = '2' where scene_qc_4 = 'Bad tissue';
update slide set scene_qc_5 = '2' where scene_qc_5 = 'Bad tissue';
update slide set scene_qc_6 = '2' where scene_qc_6 = 'Bad tissue';


update slide set scene_qc_1 = '3' where scene_qc_1 = 'End';
update slide set scene_qc_2 = '3' where scene_qc_2 = 'End';
update slide set scene_qc_3 = '3' where scene_qc_3 = 'End';
update slide set scene_qc_4 = '3' where scene_qc_4 = 'End';
update slide set scene_qc_5 = '3' where scene_qc_5 = 'End';
update slide set scene_qc_6 = '3' where scene_qc_6 = 'End';


alter table slide add column tmp_qc_1 char(1);
alter table slide add column tmp_qc_2 char(1);
alter table slide add column tmp_qc_3 char(1);
alter table slide add column tmp_qc_4 char(1);
alter table slide add column tmp_qc_5 char(1);
alter table slide add column tmp_qc_6 char(1);

update slide set tmp_qc_1 = IFNULL(scene_qc_1,0);
update slide set tmp_qc_2 = IFNULL(scene_qc_2,0);
update slide set tmp_qc_3 = IFNULL(scene_qc_3,0);
update slide set tmp_qc_4 = IFNULL(scene_qc_4,0);
update slide set tmp_qc_5 = IFNULL(scene_qc_5,0);
update slide set tmp_qc_6 = IFNULL(scene_qc_6,0);


alter table slide drop column scene_qc_1;
alter table slide drop column scene_qc_2;
alter table slide drop column scene_qc_3;
alter table slide drop column scene_qc_4;
alter table slide drop column scene_qc_5;
alter table slide drop column scene_qc_6;


alter table slide change column tmp_qc_1 scene_qc_1 tinyint not null default 0;
alter table slide change column tmp_qc_2 scene_qc_2 tinyint not null default 0;
alter table slide change column tmp_qc_3 scene_qc_3 tinyint not null default 0;
alter table slide change column tmp_qc_4 scene_qc_4 tinyint not null default 0;
alter table slide change column tmp_qc_5 scene_qc_5 tinyint not null default 0;
alter table slide change column tmp_qc_6 scene_qc_6 tinyint not null default 0;



update slide set 
insert_before_one=0,scene_qc_1=0,
insert_between_one_two=0,scene_qc_2=0,
insert_between_two_three=0,scene_qc_3=0,
insert_between_three_four=0,scene_qc_4=0,
insert_between_four_five=0,scene_qc_5=0,
insert_between_five_six=0,scene_qc_6=0


where scan_run_id =1;


alter table section add column slide_id  int(11) not null after prep_id;
