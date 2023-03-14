-- truncate tables so you can run this sql as often as you like
-- you need access to the active_atlas_production database
-- as well as the AWS version of the brainsharer database which I
-- have renamed to brainsharer_aws

DELETE FROM animal;
DELETE FROM annotation_session;

DELETE FROM auth_group;
DELETE FROM auth_group_permissions;
DELETE FROM auth_lab;
DELETE FROM auth_permission;
DELETE FROM auth_user;
DELETE FROM auth_user_groups;
DELETE FROM auth_user_labs;
DELETE FROM auth_user_user_permissions;
DELETE FROM available_neuroglancer_data;
DELETE FROM brain_atlas;
DELETE FROM brain_region;
DELETE FROM cell_type;
DELETE FROM django_admin_log;
DELETE FROM django_content_type;
DELETE FROM django_migrations;
DELETE FROM django_plotly_dash_dashapp;
DELETE FROM django_plotly_dash_statelessapp;
DELETE FROM django_session;
DELETE FROM django_site;
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


-- inserting data for table `animal`

INSERT INTO brainsharer.animal (prep_id, performance_center, date_of_birth, species, strain, sex, genotype, vender, stock_number, 
tissue_source, ship_date, shipper, tracking_number, alias, comments, active, created)
SELECT prep_id, performance_center, date_of_birth, species, strain, sex, genotype, vender, stock_number, 
tissue_source, ship_date, shipper, tracking_number, aliases_1, comments, active, created
FROM active_atlas_development.animal
ORDER BY prep_id, created;


-- TODO fill these in
-- INSERT INTO auth_group;
-- INSERT INTO auth_group_permissions;
-- INSERT INTO auth_lab;
-- INSERT INTO auth_permission;
-- INSERT INTO auth_user;
-- INSERT INTO auth_user_groups;
-- INSERT INTO auth_user_labs;
-- INSERT INTO auth_user_user_permissions;
-- INSERT INTO available_neuroglancer_data;
-- INSERT INTO brain_atlas;
-- INSERT INTO brain_region;
-- INSERT INTO cell_type;
-- INSERT INTO django_admin_log;
-- INSERT INTO django_content_type;
-- INSERT INTO django_migrations;
-- INSERT INTO django_plotly_dash_dashapp;
-- INSERT INTO django_plotly_dash_statelessapp;
-- INSERT INTO django_session;
-- INSERT INTO django_site;
-- INSERT INTO injection;
-- INSERT INTO injection_virus;
-- INSERT INTO marked_cells;
-- INSERT INTO mouselight_neuron;
-- INSERT INTO neuroglancer_state;
-- INSERT INTO polygon_sequences;
-- INSERT INTO scan_run;
-- INSERT INTO structure_com;
-- INSERT INTO viral_tracing_layer;
-- INSERT INTO virus;


-- Inserting data for table `annotation_session`

INSERT INTO brainsharer.annotation_session (id, annotation_type, FK_user_id, FK_prep_id, FK_state_id,
FK_brain_region_id, active, created, updated)
SELECT id, annotation_type, FK_annotator_id, FK_prep_id, FK_state_id,
FK_structure_id, active, created, updated
FROM active_atlas_development.annotation_session
WHERE FK_annotator_id IN (2,3,41,23,16,38,40)
ORDER BY id;
