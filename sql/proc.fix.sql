drop procedure if exists insert_previous_section;
drop procedure if exists fix_section;

DELIMITER ;;
CREATE DEFINER=`dklab`@`%` PROCEDURE `insert_previous_section`(
IN PREPID varchar(20),
IN section_number int
)
BEGIN

SET @section_number = section_number;

SET @query = CONCAT("insert into raw_section
(prep_id, section_number, tif_id, slide_physical_id, scene_number, channel, source_file, destination_file, file_status, active, created)
select
prep_id, -666 as section_number, tif_id, slide_physical_id, scene_number, channel, source_file,
CONCAT('PH_',LPAD(@section_number,4,0),'_slide_',LPAD(slide_physical_id,0,3),'S',scene_number,'_C',channel,'.tif') as destination_file,
file_status, active, NOW()
from raw_section where section_number = @section_number -1 and prep_id = '", PREPID, "'");

PREPARE stmt FROM @query;
EXECUTE stmt;



SET @query = CONCAT("update raw_section set section_number = section_number + 1
where prep_id = '", PREPID, "'
and section_number > @section_number");

PREPARE stmt FROM @query;
EXECUTE stmt;


SET @query = CONCAT("update raw_section set section_number = @section_number where section_number = -666");

PREPARE stmt FROM @query;
EXECUTE stmt;


END ;;
DELIMITER ;
