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

update slide set insert_before_one = 1,scene_qc_1 = NULL where id in (select id from slide where scene_qc_1 = 'Missing one section');
update slide set insert_between_one_two = 1,scene_qc_2 = NULL where id in (select id from slide where scene_qc_2 = 'Missing one section');
update slide set insert_between_two_three = 1,scene_qc_3 = NULL  where id in (select id from slide where scene_qc_3 = 'Missing one section');
update slide set insert_between_three_four = 1,scene_qc_4 = NULL where id in (select id from slide where scene_qc_4 = 'Missing one section');
update slide set insert_between_four_five = 1,scene_qc_5 = NULL where id in (select id from slide where scene_qc_5 = 'Missing one section');
update slide set insert_between_five_six = 1,scene_qc_6 = NULL where id in (select id from slide where scene_qc_6 = 'Missing one section');

alter table slide modify column scene_qc_1 enum("Out-of-Focus", "Bad tissue", "End") default NULL;
alter table slide modify column scene_qc_2 enum("Out-of-Focus", "Bad tissue", "End") default NULL;
alter table slide modify column scene_qc_3 enum("Out-of-Focus", "Bad tissue", "End") default NULL;
alter table slide modify column scene_qc_4 enum("Out-of-Focus", "Bad tissue", "End") default NULL;
alter table slide modify column scene_qc_5 enum("Out-of-Focus", "Bad tissue", "End") default NULL;
alter table slide modify column scene_qc_6 enum("Out-of-Focus", "Bad tissue", "End") default NULL;


alter table slide add column scenes int default null after slide_status;

alter table slide_czi_to_tif add column last_scene tinyint not null default 0; 

alter table section modify column section_qc enum("OK","Replaced", "Replace") NOT NULL default 'OK';
update section set section_qc = "Replaced" where section_qc = "Replace";
alter table section modify column section_qc enum("OK","Replaced") NOT NULL default 'OK';

-- delete from slide_czi_to_tif where file_name like 'DK39_slide%' and slide_id < 2156;
-- delete from slide where id not in (select distinct slide_id from slide_czi_to_tif where file_name like 'DK39_slide%' order by file_name) and scan_run_id = 1;

update slide set slide_physical_id = CAST(substring(file_name,11,3) as integer) where scan_run_id != 7;


ALTER TABLE slide_czi_to_tif ADD CONSTRAINT `UK__SZTT_slideid_scene__channel` UNIQUE (slide_id, scene_number, channel);

create table scene_count as 
select slide_id, cast(count(*)/3 as integer) as c from slide_czi_to_tif group by slide_id order by slide_id;

update slide S inner join scene_count SC on S.id = SC.slide_id SET S.scenes = SC.c;

drop table if exists scene_count;


alter table raw_section add column destination_file varchar(200) not null after source_file;

alter table raw_section add column scene_number int not null after section_number;

alter table section add column scene_number int not null after section_number;

alter table section add column slide_physical_id int not null after section_number;
alter table raw_section add column slide_physical_id int not null after section_number;

truncate table __file_operation;
delete from raw_section;

ALTER TABLE raw_section ADD CONSTRAINT `UK__RAWSECTION_DEST` UNIQUE (destination_file);
