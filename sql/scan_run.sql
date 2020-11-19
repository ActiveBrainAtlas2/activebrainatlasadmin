alter table scan_run add column width int(11) not null default 0 after ch_4_filter_set;
alter table scan_run add column height int(11) not null default 0 after width;
