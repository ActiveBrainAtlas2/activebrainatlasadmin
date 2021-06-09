select *
-- elab.id as label_id, el.id as labelshape_id, ej.id as job_id, elab.name, el.frame,  el.points
                from engine_job ej
                                left join engine_labeledshape el on ej.id = el.job_id 
                                                left join engine_label elab on el.label_id = elab.id
                                                                where 1=1
                                                                                and ej.id = 30
                                                                                                -- and elab.task_id = 40 
                                                                                                                -- and el.frame = 174
                                                                                                                                -- order by elab.name, el.frame;
                                                                                                                                
                                                                                                                                select * from engine_label el where el.task_id = 6;
                                                                                                                                select * from engine_labeledshape;
                                                                                                                                
                                                                                                                                select * from engine_job ej 
                                                                                                                                where ej.id = 30;
                                                                                                                                
                                                                                                                                
                                                                                                                                select group_concat( concat(x,',',y) ) as coords, section
                                                                                                                                from layer_data
                                                                                                                                where prep_id  = 'DK52'
                                                                                                                                and layer = 'Premotor'
                                                                                                                                group by section
                                                                                                                                order by prep_id, person_id, layer;
                                                                                                                                
                                                                                                                                select x,y
                                                                                                                                from layer_data ld
                                                                                                                                where prep_id  = 'DK52'
                                                                                                                                and layer = 'Premotor'
                                                                                                                                and section = 94;
                                                                                                                                
                                                                                                                                
