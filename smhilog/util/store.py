import sqlite3 as lite
import sys

from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('smhilog.sqlite3')

import time
import datetime

@db.func()
def make_date(datein, timein):
    return int(time.mktime(datetime.datetime.strptime("{0} {1}".format(datein, timein), "%Y-%m-%d %H:%M:%S").timetuple()) * 1000)

@db.func()
def make_str(timestampin):
    return ("{:%F %H:%M:%S}".format(datetime.datetime.fromtimestamp(timestampin)))

def test():
    print db.execute_sql('SELECT make_date(datum, tid), make_str(make_date(datum, tid)), datum, tid  from imp limit 10').fetchall()
    # OUTPUT: (-2523015414799391104,)

    print db.execute_sql('SELECT strftime("%Y-%m-%d", "now")').fetchone()
    
    print db.execute_sql('SELECT datum, tid from imp').fetchone()
    # OUTPUT: ('2014-12-02',)

def import_wind():

    #CREATE TABLE imp(datum text, tid text, vindriktning varchar(10), kvalitet varchar(10) ,vindhastighet varchar(10), kvalitet2 varchar(10), station varchar(10) );
    #CREATE TABLE "observations" (date_key text, station_key integer, parameter_key integer, depth_key, value real, quality varchar(1), parameter_name text, station_name text, source varchar(10), position text);
    
    db.execute_sql('insert or ignore into observations2 (date_key, station_key, parameter_key, depth_key, value, quality, parameter_name,  station_name, source, position)  SELECT make_date(datum, tid), station, 3 ,"" ,vindriktning, kvalitet, "", "", "metobs-h" ,"" from imp')
    db.execute_sql('insert or ignore into observations2 (date_key, station_key, parameter_key, depth_key, value, quality, parameter_name,  station_name, source, position)  SELECT make_date(datum, tid), station, 4 ,"" ,vindhastighet, kvalitet2, "", "", "metobs-h" ,"" from imp')
    
def delete_old():
   
    print db.execute_sql('select * from imp where make_date(datum, tid) < 31152000 limit 1000').fetchall()
    
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
    
class Store():
   
   def __init__(self, db_file):
      self.db_file = db_file

   def __enter__(self):
      return self

   def __exit__(self, exc_type, exc_val, exc_tb):
      pass
      
   def save_to_db(self, row_data):
       with lite.connect(self.db_file) as con:
           cur = con.cursor()
           cur.executemany('insert or replace into observations (date_key, station_key, parameter_key, depth_key, value, quality, parameter_name, station_name, source, position) values(?,?,?,?,?,?,?,?,?,?)', row_data) 
           con.commit();
      
   def get_dates(self):
       with lite.connect(self.db_file) as con:
           cur = con.cursor()
           cur.execute('select distinct date_key from observations')
           return cur.fetchall()
           
   def get_data(self, date_key):
       with lite.connect(self.db_file) as con:
           con.row_factory = dict_factory
           cur = con.cursor()
           cur.execute('select * from observations where date_key=?', (date_key,))
           return cur.fetchall()
   
   def process_import(self):
       pass
