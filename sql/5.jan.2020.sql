alter table scan_run add column rotation int not null default 0 after height;
alter table scan_run add column flip enum('none', 'flip', 'flop') not null default 'none' after rotation;
