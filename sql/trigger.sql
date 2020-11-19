delimiter //
drop trigger if exists b_section //

create trigger b_section before insert on raw_section
for each row begin
  set @auto_id := 1; 

-- SET max_id=(SELECT MAX(agent_id_pk)+1 FROM `agent_mst`);
    IF (new.section_number IS NULL) THEN
        @auto_id = 1;
    END IF;


  set new.section_number = @auto_id + 3;
end;
//

delimiter ;
