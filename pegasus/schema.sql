drop table if exists users;
create table users (
  id integer primary key autoincrement,
  name text,
  username text unique not null,
  password text not null,
  email text unique not null,
  join_date datetime default current_timestamp
);