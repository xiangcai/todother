-- To create the database:
--    CREATE DATABASE withme;
--    GRANT ALL PRIVILEGES ON withme.* to 'withme'@'localhost' IDENTIFIED BY 'withme';
--
-- Then load the schema to create tables:
--    mysql -u withme -pwithme withme < schema.sql

SET SESSION storage_engine = "InnoDB";
SET SESSION time_zone = "+8:00";
ALTER DATABASE CHARACTER SET "utf8";

DROP TABLE IF EXISTS auth_user;
CREATE TABLE auth_user (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(12) NOT NULL UNIQUE,
    gender VARCHAR(10),
    email VARCHAR(100) NOT NULL UNIQUE,
    mobile VARCHAR(11),
    nickname VARCHAR(100) NOT NULL,
    realname VARCHAR(100),
    language VARCHAR(10) DEFAULT "zh_CN",
    password BLOB NOT NULL,
    user_level INT DEFAULT 0,
    KEY (`user_id`),
    KEY (`email`),
    KEY (`mobile`)
);

DROP TABLE IF EXISTS todo;
CREATE TABLE  todo (
  todo_id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
  todo_created_date datetime NOT NULL,
  todo_user_id varchar(12),
  todo_what varchar(200) NOT NULL,
  todo_when varchar(100) NOT NULL,
  todo_target_date date,
  todo_location_longtiude int(11),
  todo_location_lantitude int(11),
  todo_remind int(11) NOT NULL DEFAULT 0,
  todo_like int(11) NOT NULL DEFAULT 0,
  todo_group_id int(11),
  todo_pic_path varchar(100),
  todo_type int(11) NOT NULL DEFAULT 1,
  todo_status int(11) NOT NULL DEFAULT 0,
  todo_closed_date datetime,
  todo_category int(11) NOT NULL DEFAULT 0,
  todo_viewed int(11) NOT NULL DEFAULT 0,
  todo_slug varchar(40) NOT NULL,
  todo_updated_date datetime
)
