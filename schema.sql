drop table if exists consumer;
create table consumer (
    id integer primary key autoincrement,
    email text not null
);
