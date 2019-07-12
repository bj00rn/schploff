#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
import sqlite3 as lite
import sys

from loguru import logger


class NoStore():
    def __init__(self):
        logger.warning('No database specified')
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def get(self, *arg, **kwargs):
        return None

    def add(self, *args, **kwargs):
        return True

    def exists(self, *arg, **kwargs):
        return False


class SqliteStore():
    def __init__(self, db_file):
        self.con = lite.connect(db_file)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def get(self, hash):
        cur = self.con.cursor()
        cur.execute('SELECT * from download where hash=?', (hash, ))
        data = cur.fetchone()
        return data

    def add(self, hash, timestamp, filename, file_class):
        cur = self.con.cursor()
        cur.execute('insert into download values(?,?,?,?)',
                    (hash, timestamp, filename, file_class))
        self.con.commit()
        logger.info('added [{hash}] [{filename}] to database'.format(
            hash=hash, filename=filename))
        return True

    def remove(self, hash):
        cur = self.con.cursor()
        cur.execute('DELETE FROM download WHERE hash=?', (hash, ))
        self.con.commit()
        logger.info('deleted [{hash}] from database'.format(hash=hash))
        return True

    def updated(self, file_class):
        cur = self.con.cursor()
        cur.execute(
            'SELECT timestamp FROM download where fileclass=? ORDER BY timestamp DESC LIMIT 1',
            (file_class, ))
        return cur.fetchone()

    def exists(self, hash):
        return self.get(hash) is not None
