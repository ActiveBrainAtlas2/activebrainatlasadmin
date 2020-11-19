alter table slide modify column scene_qc_1 enum("O-o-F","Replace", "End","Bad tissue","Missing one section") default NULL;
alter table slide modify column scene_qc_2 enum("O-o-F","Replace", "End","Bad tissue","Missing one section") default NULL;
alter table slide modify column scene_qc_3 enum("O-o-F","Replace", "End","Bad tissue","Missing one section") default NULL;
alter table slide modify column scene_qc_4 enum("O-o-F","Replace", "End","Bad tissue","Missing one section") default NULL;
alter table slide modify column scene_qc_5 enum("O-o-F","Replace", "End","Bad tissue","Missing one section") default NULL;
alter table slide modify column scene_qc_6 enum("O-o-F","Replace", "End","Bad tissue","Missing one section") default NULL;

update slide set scene_qc_1 = 'Replace' where scene_qc_1 is not null;
update slide set scene_qc_2 = 'Replace' where scene_qc_2 is not null;
update slide set scene_qc_3 = 'Replace' where scene_qc_3 is not null;
update slide set scene_qc_4 = 'Replace' where scene_qc_4 is not null;
update slide set scene_qc_5 = 'Replace' where scene_qc_5 is not null;
update slide set scene_qc_6 = 'Replace' where scene_qc_6 is not null;

alter table slide modify column scene_qc_1 enum("Replace", "End") default NULL;
alter table slide modify column scene_qc_2 enum("Replace", "End") default NULL;
alter table slide modify column scene_qc_3 enum("Replace", "End") default NULL;
alter table slide modify column scene_qc_4 enum("Replace", "End") default NULL;
alter table slide modify column scene_qc_5 enum("Replace", "End") default NULL;
alter table slide modify column scene_qc_6 enum("Replace", "End") default NULL;

alter table slide add column scenes int default null after slide_status;

alter table slide_czi_to_tif add column last_scene tinyint not null default 0; 

alter table section modify column section_qc enum("OK","Replaced", "Replace") NOT NULL default 'OK';
update section set section_qc = "Replaced" where section_qc = "Replace";
alter table section modify column section_qc enum("OK","Replaced") NOT NULL default 'OK';
