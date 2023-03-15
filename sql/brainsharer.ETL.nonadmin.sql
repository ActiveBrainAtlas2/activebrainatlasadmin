-- truncate tables so you can run this sql as often as you like
-- you need access to the active_atlas_production database
-- as well as the AWS version of the brainsharer database which I
-- have renamed to brainsharer_aws

TRUNCATE brainsharer.available_neuroglancer_data;
TRUNCATE brainsharer.marked_cells;
DELETE FROM brain_region;
DELETE FROM brainsharer.brain_atlas;
INSERT INTO brainsharer.brain_atlas (id, active, created, atlas_name, description, FK_lab_id, resolution, zresolution, url)
values (1, 1, NOW(), 'DKLAB Atlas', 'The 10um isotropic atlas from the Kleinfeld lab', 1, 10, 10, 'NA');

DELETE FROM annotation_session;
DELETE FROM available_neuroglancer_data;
DELETE FROM cell_type;
DELETE FROM injection;
DELETE FROM injection_virus;
DELETE FROM marked_cells;
DELETE FROM mouselight_neuron;
DELETE FROM neuroglancer_state;
DELETE FROM polygon_sequences;
DELETE FROM scan_run;
DELETE FROM structure_com;
DELETE FROM viral_tracing_layer;
DELETE FROM virus;
DELETE FROM animal;

-- inserting data for table `animal`

INSERT INTO brainsharer.animal (prep_id, performance_center, date_of_birth, species, strain, sex, genotype, vender, stock_number, 
tissue_source, ship_date, shipper, tracking_number, alias, comments, active, created)
SELECT prep_id, performance_center, date_of_birth, species, strain, sex, genotype, vender, stock_number, 
tissue_source, ship_date, shipper, tracking_number, aliases_1, comments, active, created
FROM active_atlas_production.animal
ORDER BY prep_id, created;


-- TODO fill these in
INSERT INTO brainsharer.available_neuroglancer_data SELECT * FROM brainsharer_aws.available_neuroglancer_data;
INSERT INTO brainsharer.brain_atlas SELECT * FROM brainsharer_aws.brain_atlas;
-- brain region needs a full select
INSERT INTO brainsharer.brain_region (id,active,created,abbreviation,description,FK_ref_atlas_id)
select id, active , created , abbreviation , description, 1 as FK_ref_atlas_id 
FROM active_atlas_production.structure; 


INSERT INTO brainsharer.cell_type SELECT * FROM active_atlas_production.cell_type;
-- injection needs full insert
INSERT INTO brainsharer.injection (id,active,created,
anesthesia, method, pipet, location, angle,
brain_location_dv, brain_location_ml, brain_location_ap, injection_date, transport_days,
virus_count, comments, injection_volume, FK_prep_id, FK_performance_center_id)
SELECT inj.id, inj.active , inj.created ,  
anesthesia, method, pipet, location, angle,
brain_location_dv, brain_location_ml, brain_location_ap, injection_date, transport_days,
virus_count, inj.comments, injection_volume, a.prep_id as FK_prep_id, 2 as FK_performance_center_id
FROM active_atlas_production.injection inj
INNER JOIN active_atlas_production.animal a on inj.prep_id = a.prep_id;



INSERT INTO brainsharer.injection_virus select id , injection_id , virus_id ,  
DATE(DATE_FORMAT(created, '%Y-%m-%d %H:%i:%s')) AS created, active 
from active_atlas_production.injection_virus;

INSERT INTO brainsharer.marked_cells SELECT * FROM active_atlas_production.marked_cells;
INSERT INTO brainsharer.mouselight_neuron SELECT * FROM brainsharer_aws.mouselight_neuron;
INSERT INTO brainsharer.neuroglancer_state SELECT * FROM active_atlas_production.neuroglancer_state;
INSERT INTO brainsharer.polygon_sequences SELECT * FROM active_atlas_production.polygon_sequences;
INSERT INTO brainsharer.scan_run SELECT * FROM active_atlas_production.scan_run;
INSERT INTO brainsharer.structure_com SELECT * FROM active_atlas_production.structure_com;
INSERT INTO brainsharer.viral_tracing_layer SELECT * FROM brainsharer_aws.viral_tracing_layer;
INSERT INTO brainsharer.virus SELECT * FROM active_atlas_production.virus;


-- Inserting data for table `annotation_session`

INSERT INTO brainsharer.annotation_session (id, annotation_type, FK_user_id, FK_prep_id, FK_state_id,
FK_brain_region_id, active, created, updated)
SELECT id, annotation_type, FK_annotator_id, FK_prep_id, FK_state_id,
FK_structure_id, active, created, updated
FROM active_atlas_development.annotation_session
WHERE FK_annotator_id IN (2,3,41,23,16,38,40)
ORDER BY id;
