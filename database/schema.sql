-- To create the database:
--    CREATE DATABASE withme;
--    GRANT ALL PRIVILEGES ON withme.* to withme@localhost IDENTIFIED BY withme;
--
-- Then load the schema to create tables:
--    mysql -u withme -pwithme withme < schema.sql


DROP TABLE IF EXISTS todo;
CREATE TABLE  todo (
  todo_id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  todo_created_date datetime NOT NULL,
  todo_user_id varchar(12) DEFAULT NULL,
  todo_what varchar(200) NOT NULL,
  todo_when varchar(100) NOT NULL,
  todo_target_date date DEFAULT NULL,
  todo_location_longtiude int(11) DEFAULT NULL,
  todo_location_lantitude int(11) DEFAULT NULL,
  todo_remind int(11) NOT NULL DEFAULT 0,
  todo_like int(11) NOT NULL DEFAULT 0,
  todo_group_id int(11) DEFAULT NULL,
  todo_pic_path varchar(100) DEFAULT NULL,
  todo_type int(11) NOT NULL DEFAULT 2,
  todo_status int(11) NOT NULL DEFAULT 0,
  todo_closed_date datetime DEFAULT NULL,
  todo_category int(11) NOT NULL DEFAULT 0,
  todo_viewed int(11) NOT NULL DEFAULT 0,
  todo_slug varchar(20) NOT NULL,
  todo_updated_date datetime DEFAULT NULL
)
