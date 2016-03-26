drop table if exists users;
create table users (
  id integer primary key autoincrement,
  name text,
  username text unique not null,
  password text not null,
  email text unique not null,
  join_date datetime default current_timestamp
);

drop table if exists boards;
create table boards (
	id integer primary key autoincrement,
	title text not null,
	creatorID integer not null,
	created_at datetime default current_timestamp,
	done_at datetime, /* how are we going to set this to 'tomorrow'? */
	FOREIGN KEY(creatorID) REFERENCES users(id)
);

drop table if exists board_content;
create table board_content (
	id integer primary key autoincrement,
	boardID integer not null,
	content text not null,
	userID integer not null,
	FOREIGN KEY (boardID) REFERENCES boards(id),
	FOREIGN KEY (userID) REFERENCES users(id)
);

drop table if exists invites;
create table invites (
	id integer primary key autoincrement,
	boardID integer not null,
	userEmail text not null,
	invite_date datetime default current_timestamp,
	type text check(type = 'view' or type = 'edit'),
	FOREIGN KEY (boardID) REFERENCES boards(id),
	FOREIGN KEY (userEmail) REFERENCES users(email)
);