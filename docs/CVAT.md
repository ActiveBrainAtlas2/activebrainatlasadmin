### CVAT install into existing django project
#### Libraries
1. pip install git+https://github.com/openvinotoolkit/datumaro@v0.1.0
1. diskcache
1. logstash
#### Database
1. alter table auth_user modify column first_name varchar(150)
1. drop table engine_plugin
1. drop table engine_pluginoption
1. alter table engine_data add column storage_method varchar(15)

