import urllib
import json
import sqlite3 as lite

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def fetchParameter(source, station, parameter, period):
  url="https://opendata-download-{source}.smhi.se/api/version/latest/parameter/{parameter}/station/{station}/period/{period}/data.json".format(station=station, parameter=parameter, source=source, period=period)
  print("fetching {url} ... ".format(url=url))
  response = urllib.urlopen(url)
  data = json.loads(response.read())
  data["source"] = source
  return data

def json_to_tuple(json_data):
   (value, updated, parameter, station, period, position, link, source, position) = (json_data["value"], json_data["updated"], json_data["parameter"], json_data["station"], json_data["period"], json_data["position"], json_data["link"], json_data["source"], str(json_data["position"][0]["latitude"]) + ',' + str(json_data["position"][0]["longitude"]))
   
   rows = []
   
   for v in value:
      date_key = v["date"]
      station_key = station["key"]
      parameter_key = parameter["key"]
      
      if v.has_key('depth'): #depth only in ocobs
         depth = v['depth']
      else:
         depth = '-'
         
      value = v["value"]
      quality = v["quality"]
      parameter_name = parameter["name"]
      station_name = station["name"]
      
      rows.append((date_key, station_key, parameter_key, depth, value , quality, parameter_name, station_name, source, position))
   return rows
   