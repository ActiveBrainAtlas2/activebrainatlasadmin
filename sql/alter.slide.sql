alter table slide add column insert_before_one tinyint not null default 0 after slide_status;
alter table slide add column insert_between_one_two tinyint not null default 0 after scene_qc_1;
alter table slide add column insert_between_two_three tinyint not null default 0 after scene_qc_2;
alter table slide add column insert_between_three_four tinyint not null default 0 after scene_qc_3;
alter table slide add column insert_between_four_five tinyint not null default 0 after scene_qc_4;
alter table slide add column insert_between_five_six tinyint not null default 0 after scene_qc_5;

alter table slide modify column scene_qc_1 enum("Out-of-Focus", "Bad tissue","O-o-F","Missing one section") default NULL;
alter table slide modify column scene_qc_2 enum("Out-of-Focus", "Bad tissue","O-o-F","Missing one section") default NULL;
alter table slide modify column scene_qc_3 enum("Out-of-Focus", "Bad tissue","O-o-F","Missing one section") default NULL;
alter table slide modify column scene_qc_4 enum("Out-of-Focus", "Bad tissue","O-o-F","Missing one section") default NULL;
alter table slide modify column scene_qc_5 enum("Out-of-Focus", "Bad tissue","O-o-F","Missing one section") default NULL;
alter table slide modify column scene_qc_6 enum("Out-of-Focus", "Bad tissue","O-o-F","Missing one section") default NULL;

update slide set scene_qc_1 = 'Out-of-Focus' where scene_qc_1 = 'O-o-F';
update slide set scene_qc_2 = 'Out-of-Focus' where scene_qc_2 = 'O-o-F';
update slide set scene_qc_3 = 'Out-of-Focus' where scene_qc_3 = 'O-o-F';
update slide set scene_qc_4 = 'Out-of-Focus' where scene_qc_4 = 'O-o-F';
update slide set scene_qc_5 = 'Out-of-Focus' where scene_qc_5 = 'O-o-F';
update slide set scene_qc_6 = 'Out-of-Focus' where scene_qc_6 = 'O-o-F';

update slide set insert_before_one = 1, scene_qc_1 = NULL where id in (select id from slide where scene_qc_1 = 'Missing one section');
update slide set insert_between_one_two = 1, scene_qc_2 = NULL where id in (select id from slide where scene_qc_2 = 'Missing one section');
update slide set insert_between_two_three = 1, scene_qc_3 = NULL where id in (select id from slide where scene_qc_3 = 'Missing one section');
update slide set insert_between_three_four = 1, scene_qc_4 = NULL where id in (select id from slide where scene_qc_4 = 'Missing one section');
update slide set insert_between_four_five = 1, scene_qc_5 = NULL where id in (select id from slide where scene_qc_5 = 'Missing one section');
update slide set insert_between_five_six = 1, scene_qc_6 = NULL where id in (select id from slide where scene_qc_6 = 'Missing one section');

alter table slide modify column scene_qc_1 enum("Out-of-Focus", "Bad tissue") default NULL;
alter table slide modify column scene_qc_2 enum("Out-of-Focus", "Bad tissue") default NULL;
alter table slide modify column scene_qc_3 enum("Out-of-Focus", "Bad tissue") default NULL;
alter table slide modify column scene_qc_4 enum("Out-of-Focus", "Bad tissue") default NULL;
alter table slide modify column scene_qc_5 enum("Out-of-Focus", "Bad tissue") default NULL;
alter table slide modify column scene_qc_6 enum("Out-of-Focus", "Bad tissue") default NULL;

