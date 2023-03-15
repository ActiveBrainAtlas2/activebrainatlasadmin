-- Steps:
-- DROP database brainsharer;
-- CREATE database brainsharer;
-- mysql brainsharer < brainsharer.v1.1.sql
-- run this sql file
--  the Django admin tables so you can run this sql as often as you like
-- you need access to the active_atlas_production database
-- as well as the AWS version of the brainsharer database which I
-- have renamed to brainsharer_aws


-- insert the Django admin stuff first
-- auth user
INSERT INTO brainsharer.django_content_type SELECT * FROM active_atlas_production.django_content_type;
INSERT INTO brainsharer.auth_user SELECT * FROM active_atlas_production.auth_user;
INSERT INTO brainsharer.auth_group SELECT * FROM active_atlas_production.auth_group;
INSERT INTO brainsharer.auth_permission SELECT * FROM active_atlas_production.auth_permission;
INSERT INTO brainsharer.auth_group_permissions SELECT * FROM active_atlas_production.auth_group_permissions;

INSERT INTO brainsharer.auth_lab SELECT * FROM brainsharer_aws.auth_lab;
INSERT INTO brainsharer.auth_user_groups SELECT * FROM active_atlas_production.auth_user_groups;
INSERT INTO brainsharer.auth_user_labs SELECT * FROM brainsharer_aws.auth_user_labs;
INSERT INTO brainsharer.auth_user_user_permissions SELECT * FROM active_atlas_production.auth_user_user_permissions;

INSERT INTO brainsharer.django_admin_log SELECT * FROM active_atlas_production.django_admin_log;
-- INSERT INTO brainsharer.django_migrations SELECT * FROM active_atlas_production.django_;
INSERT INTO brainsharer.django_plotly_dash_dashapp SELECT * FROM active_atlas_production.django_plotly_dash_dashapp;
INSERT INTO brainsharer.django_plotly_dash_statelessapp SELECT * FROM active_atlas_production.django_plotly_dash_statelessapp;
INSERT INTO brainsharer.django_session SELECT * FROM active_atlas_production.django_session;
INSERT INTO brainsharer.django_site SELECT * FROM active_atlas_production.django_site;
