# web_dev
use web_dev;
create table if not exists users(
    id integer not null auto_increment,
    name varchar(32),
    fullname varchar(128),
    nickname varchar(32),
    create_time datetime,
    primary key (id)
);

# web_dev2
use web_dev2;
create table if not exists address (
    id integer not null auto_increment,
    email varchar(64),
    user_id integer,
    primary key (id)
);

create index user_id_inx on address (user_id);
