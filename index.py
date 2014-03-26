#-*-coding: utf-8 -*-
#!/usr/bin/python
import sqlite3
from contextlib import closing

from flask import Flask, request, render_template, send_from_directory, flash, g, redirect, url_for
import os
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding("utf-8")


app = Flask(__name__)
app.config.from_pyfile('config.cfg')


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
    g.db.close()


def list_factory(cursor, row):
    list = []
    for idx, col in enumerate(cursor.description):
        list.append(row[idx])
    return list


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def db_query(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def db_insert(sql,args=()):
    g.db.execute(sql,args)
    g.db.commit()


def db_delete(sql,args=()):
    g.db.execute(sql,args)
    g.db.commit()


@app.route('/ask', methods=['POST'])
def ask_for_code():
    email = request.form['email']
    hasAsk = db_query('select email from consumer where email =?', [email], one=True)
    if hasAsk:
        flash('您已经索码成功，请耐心等待！')
    else:
        db_insert('insert into consumer(email) values (?)',[email])
        flash('索码成功，如果有人赠码，会第一时间发送给您！')
    return redirect(url_for('index'))


@app.route('/donate', methods=['POST'])
def donate():
    count = request.form['count']
    result = db_query('select email from consumer order by id limit ?',[count])
    print result
    if not result:
        flash('暂时没有人索码，请您稍后回来！')
    count = db_query('select count(*) from consumer', one=True)[0]
    return render_template('index.html', result=result, count = count, active=0)


@app.route('/complete', methods=['POST'])
def complete():
    print request.form
    emails = request.form.getlist('email')
    print 'delete from consumer where email in (%s?)' % ('?,'* (len(emails)-1))
    db_delete('delete from consumer where email in (%s?)' % ('?,'* (len(emails)-1)), emails)
    flash('感谢您的分享精神！')
    return redirect(url_for('index'))


@app.route('/')
def index():
    count = db_query('select count(*) from consumer', one=True)[0]
    return render_template('index.html', count = count, active=0)


@app.route('/about')
def about():
    return render_template('about.html', active=1)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
            'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run()
