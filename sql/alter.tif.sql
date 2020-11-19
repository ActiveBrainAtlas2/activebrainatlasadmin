alter table slide_czi_to_tif add column processing_duration float not null default 0;
alter table slide drop column processing_duration;
