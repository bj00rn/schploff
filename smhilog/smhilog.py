#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import util.smhi as smhi
from util.store import Store

def main():
   dir = os.path.dirname(__file__)
   db_file = os.path.join(dir, 'smhilog.sqlite3')
   
   with Store(db_file) as store:
       store.save_to_db(smhi.json_to_tuple(smhi.fetchParameter('ocobs', '33008' ,'1', 'latest-day')))
       store.save_to_db(smhi.json_to_tuple(smhi.fetchParameter('ocobs', '33008' ,'9', 'latest-day')))
       store.save_to_db(smhi.json_to_tuple(smhi.fetchParameter('ocobs', '33008' ,'8', 'latest-day')))
       store.save_to_db(smhi.json_to_tuple(smhi.fetchParameter('ocobs', '33002' ,'1', 'latest-day')))
       store.save_to_db(smhi.json_to_tuple(smhi.fetchParameter('ocobs', '33002' ,'9', 'latest-day')))
       store.save_to_db(smhi.json_to_tuple(smhi.fetchParameter('ocobs', '33002' ,'7', 'latest-day')))
       
       #landsort
       store.save_to_db(smhi.json_to_tuple(smhi.fetchParameter('metobs', '87440' ,'3', 'latest-day')))
       store.save_to_db(smhi.json_to_tuple(smhi.fetchParameter('metobs', '87440' ,'4', 'latest-day')))
       
       #oland
       store.save_to_db(smhi.json_to_tuple(smhi.fetchParameter('metobs', '77210' ,'3', 'latest-day')))
       store.save_to_db(smhi.json_to_tuple(smhi.fetchParameter('metobs', '77210' ,'4', 'latest-day')))
   
   
   
if __name__ == "__main__": main()
   