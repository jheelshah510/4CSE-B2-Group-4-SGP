import sqlite3

con = sqlite3.connect('dockat.db')

cur = con.cursor()


cur.execute("CREATE TABLE IF NOT EXISTs login (user_id INTEGER PRIMARY KEY AUTOINCREMENT,username varchar(50),password varchar(50));")
cur.execute("CREATE TABLE IF NOT EXISTs tokens (token varchar(41) PRIMARY KEY,user_id INTEGER);")

cur.execute("CREATE TABLE IF NOT EXISTs documents (doc_id varchar(10) primary key,doc_name text,description text,owner integer,tags text,md5_checksum text,original_md5 text,file_path text,original_path text,original_name text);")

cur.execute("create table if not exists tags (tag_id INTEGER PRIMARY KEY AUTOINCREMENT,tag_name varchar(30),tag_color varchar(10),owner INTEGER);")
cur.execute("create table if not exists usertags (tag_id INTEGER,user_id INTEGER,write INTEGER);")
cur.execute("create table if not exists tags_ref (tag_id INTEGER,doc_id varchar(10));")
cur.execute("CREATE virtual TABLE IF NOT EXISTS contents using fts5(doc_id,file_contents);")

cur.execute("Create table if not exists share (share_id varchar(20),doc_id varchar(10),user_id integer);")
cur.execute("INSERT INTO login (username,password) VALUES ('tarang','sgp');")



cur.execute("commit;")

