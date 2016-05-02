drop table if exists invites;
drop table if exists board_content;
drop table if exists boards;
drop table if exists users;

create table users (
  id integer primary key autoincrement,
  name text,
  username text unique not null,
  password text not null,
  email text unique not null,
  join_date datetime default current_timestamp
);


create table boards (
	id integer primary key autoincrement,
	title text not null,
	creatorID integer not null,
	created_at datetime default current_timestamp,
	done_at datetime, 
	locked_until datetime default current_timestamp, /* for some reason datetime in this particular field randomly fucks up */
	locked_by text,  /* UserID for logged in, or Email for Invited */
	FOREIGN KEY(creatorID) REFERENCES users(id)
);


create table board_content (
	id integer primary key autoincrement,
	boardID integer not null,
	content text not null,
	type text not null,
	userID integer, /* null if user is not logged in */
	userEmail text, /* only has values if user is not logged in, not refreshed if user is registered/changed address/etc */
	created_at datetime default current_timestamp,
	last_modified_at datetime,
	last_modified_by text, /* UserID for logged in, or Email for Invited */
	position text,
	deleted text default 'N',
	FOREIGN KEY (boardID) REFERENCES boards(id) ON DELETE CASCADE,
	FOREIGN KEY (userID) REFERENCES users(id)
);


create table invites (
	id varchar(32) primary key, /* randomly generated string on the server */
	boardID integer not null,
	userEmail text not null,
	invite_date datetime default current_timestamp,
	type text check(type = 'view' or type = 'edit'),
	FOREIGN KEY (boardID) REFERENCES boards(id) ON DELETE CASCADE,
	UNIQUE (userEmail, boardID)
	/*FOREIGN KEY (userEmail) REFERENCES users(email)*/ /* Removed constraint to invite people who don't have accounts yet, if a user were to change their email in their account cascading would have to be done manually */
);

