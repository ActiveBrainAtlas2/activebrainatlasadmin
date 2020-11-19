alter table slide_czi_to_tif drop column last_scene;

alter table section add column tif_id int not null after section_number;
alter table raw_section add column tif_id int not null after section_number;



ALTER TABLE raw_section
ADD CONSTRAINT `FK__RS_TIFID` 
FOREIGN KEY (tif_id) REFERENCES slide_czi_to_tif(id)
ON UPDATE CASCADE
ON DELETE CASCADE;

