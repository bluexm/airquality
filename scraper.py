import pandas as pd
import requests
import bs4 
import sqlite3
import json 


DB_FILE = "data.sqlite"
DB_TITLES = ["station","reading"]

import sqlite3
from sqlite3 import Error
try:
    CONNEXION = sqlite3.connect(DB_FILE)
    print("connexion with DB successful, using SQLlite ", sqlite3.version)
except Error as e:
    print(e)

dfdb = pd.DataFrame(columns=DB_TITLES)
# or read column titles from database 
try:
    curDB = pd.read_sql("select * from indeed_ads", CONNEXION)
except:
    print("database empty")
    curDB = None


#------------- Scraping ------------------------
urlstations=['https://api.waqi.info/map/bounds/?token=7c88a4e043854ed6beeb8e06052616ef3d0fd01f&latlng=22.29,113.37,22.03,113.92']

response = requests.get(urlstations[0])
json_raw = json.loads(response.text)
data=json_raw["data"]


#------------- Saving in DB ------------------------

dfdb.to_sql('indeed_ads',CONNEXION,if_exists='append', index=False)
print('{:d} new ads recorded'.format(len(dfdb)))
CONNEXION.close()

