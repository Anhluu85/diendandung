from flask import g
import sqlite3
import os
import config

DATABASE = config.DATABASE

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    with open(os.path.join(os.path.dirname(__file__), '..', 'schema.sql'), mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()
    print(f"Database '{DATABASE}' created and schema initialized.")

def check_and_init_db(app):
    if not os.path.exists(DATABASE):
        with app.app_context():
            init_db()
            print(f"Đã tạo file cơ sở dữ liệu: {DATABASE} và khởi tạo schema.")
    else:
        print(f"Database '{DATABASE}' already exists.")
