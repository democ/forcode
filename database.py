#-*-coding: utf-8 -*-
#!/usr/bin/python
# all the imports
import sqlite3

#configuration
DATABASE = 'forcode.db'


def connect_db():
    conn = sqlite3.connect(DATABASE)
    return conn.cursor()

def db_query(query, args=(), one=False):
    result = connect_db().execute(query, args)
    rv = result.fetchall()
    result.close()
    return (rv[0] if rv else None) if one else rv

def db_insert(sql,args=()):
    connect_db().execute(sql,args)

def db_delete(sql,args=()):
    connect_db().execute(sql,args)

if __name__ == "__main__":
    print db_query("select * from consumer;")
