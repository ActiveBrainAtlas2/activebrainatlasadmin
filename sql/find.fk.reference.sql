USE information_schema;
SELECT *
FROM
  KEY_COLUMN_USAGE
  WHERE
    REFERENCED_TABLE_NAME = 'task'
    AND REFERENCED_TABLE_SCHEMA = 'active_atlas_development'
--      AND REFERENCED_COLUMN_NAME = 'X_id'
\G
