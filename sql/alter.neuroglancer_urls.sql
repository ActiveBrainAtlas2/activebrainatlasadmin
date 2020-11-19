alter table neuroglancer_urls add column vetted tinyint(1) not null default 0 after active;
alter table neuroglancer_urls add column person_id int(11) NOT NULL after id;
-- KEY schedule_person_id_9f59b05d_fk_auth_user_id (person_id),
-- CONSTRAINT schedule_person_id_9f59b05d_fk_auth_user_id FOREIGN KEY (person_id) REFERENCES auth_user (id)

ALTER TABLE neuroglancer_urls ADD INDEX K__NU (person_id);

ALTER TABLE neuroglancer_urls ADD CONSTRAINT FK__NU_user_id foreign key (id) references auth_user(id) on update cascade;
