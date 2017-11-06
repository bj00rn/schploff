#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3 as lite
import sys


class Store():

    def __init__(self, db_file):
        self.con = lite.connect(db_file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def get(self, hash):
        cur = self.con.cursor()
        cur.execute('SELECT * from download where hash=?', (hash,))
        data = cur.fetchone()
        return data

    def add(self, hash, timestamp, filename, file_class):
        cur = self.con.cursor()
        cur.execute('insert into download values(?,?,?,?)',
                    (hash, timestamp, filename, file_class))
        self.con.commit()
        return True

    def remove(self, hash):
        cur = self.con.cursor()
        cur.execute("DELETE FROM download WHERE hash=?", (hash,))
        self.con.commit()
        return True

    def updated(self, file_class):
        cur = self.con.cursor()
        cur.execute(
            "SELECT timestamp FROM download where fileclass=? ORDER BY timestamp DESC LIMIT 1", (file_class,))
        return cur.fetchone()
