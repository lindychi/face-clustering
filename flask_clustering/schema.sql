DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS cluster;
DROP TABLE IF EXISTS face;
DROP TABLE IF EXISTS file;
DROP TABLE IF EXISTS tag;
DROP TABLE IF EXISTS tag_unit;
DROP TABLE IF EXISTS asyn_path;

CREATE TABLE user (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT UNIQUE NOT NULL,
       password TEXT NOT NULL
);

CREATE TABLE cluster (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       name TEXT NOT NULL,
       created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,	
       total INTEGER DEFAULT 0,
       FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE face (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       cluster_id INTEGER NOT NULL DEFAULT -1,
       file_id INTEGER NOT NULL,
       face_index INTEGER NOT NULL,
       level INTEGER DEFAULT 0,
       top INTEGER DEFAULT 0,
       right INTEGER DEFAULT 0,
       bottom INTEGER DEFAULT 0,
       left INTEGER DEFAULT 0,
       origin_path TEXT NOT NULL,
       thumb_path TEXT NOT NULL,
       FOREIGN KEY (user_id) REFERENCES user (id),
       FOREIGN KEY (cluster_id) REFERENCES cluster (id),
       FOREIGN KEY (file_id) REFERENCES file (id)
);

CREATE TABLE file (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       uploaded TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- TODO: file created time
       path TEXT UNIQUE NOT NULL,
       name TEXT NOT NULL,
       check_level INTEGER NOT NULL DEFAULT 0,
       FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE tag (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,	
       name TEXT NOT NULL,
       FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE tag_unit (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       file_id INTEGER NOT NULL,
       tag_id INTEGER NOT NULL,
       FOREIGN KEY (user_id) REFERENCES user (id),
       FOREIGN KEY (file_id) REFERENCES file (id),
       FOREIGN KEY (tag_id) REFERENCES tag (id)
);

CREATE TABLE asyn_path (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER NOT NULL,
       name TEXT NOT NULL,
       path TEXT NOT NULL,
       created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (user_id) REFERENCES user (id)
);
