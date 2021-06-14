delete from task where lookup_id  in (110,225);
delete from progress_lookup where id = 110;

INSERT INTO task (prep_id, completed, start_date, end_date,active,created, lookup_id)
SELECT prep_id, 1, now(), now(), 1, now(), 225
FROM   animal 
WHERE  active = 1 and prep_id not in ('X', 'JT');
