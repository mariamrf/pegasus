drop table if exists items;
create table items (
  id integer primary key autoincrement,
  content text not null
);