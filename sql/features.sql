+---------------------+-------------+------+-----+---------+----------------+
| Field               | Type        | Null | Key | Default | Extra          |
+---------------------+-------------+------+-----+---------+----------------+
| id                  | bigint(20)  | NO   | PRI | NULL    | auto_increment |
| prep_id             | varchar(20) | NO   | MUL | NULL    |                |
| section             | int(11)     | NO   | MUL | NULL    |                |
| x                   | int(11)     | NO   |     | NULL    |                |
| y                   | int(11)     | NO   |     | NULL    |                |
| cell_images         | blob        | YES  |     | NULL    |                |
| DMVec1              | float       | YES  |     | NULL    |                |
| DMVec2              | float       | YES  |     | NULL    |                |
| DMVec3              | float       | YES  |     | NULL    |                |
| DMVec4              | float       | YES  |     | NULL    |                |
| DMVec5              | float       | YES  |     | NULL    |                |
| DMVec6              | float       | YES  |     | NULL    |                |
| DMVec7              | float       | YES  |     | NULL    |                |
| DMVec8              | float       | YES  |     | NULL    |                |
| DMVec9              | float       | YES  |     | NULL    |                |
| DMVec10             | float       | YES  |     | NULL    |                |
| area                | int(11)     | YES  |     | NULL    |                |
| height              | int(11)     | YES  |     | NULL    |                |
| horiz_std           | float       | YES  |     | NULL    |                |
| mean                | float       | YES  |     | NULL    |                |
| padded_size         | int(11)     | YES  |     | NULL    |                |
| rotation            | float       | YES  |     | NULL    |                |
| rotation_confidence | float       | YES  |     | NULL    |                |
| std                 | float       | YES  |     | NULL    |                |
| vert_std            | float       | YES  |     | NULL    |                |
| width               | int(11)     | YES  |     | NULL    |                |
+---------------------+-------------+------+-----+---------+----------------+
