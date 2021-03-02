#!/usr/bin/env python

import requests as rqs
import bs4 
import pandas as pd 
import json 

import logging
logging.basicConfig(filename='scrape_aqi.log',level=logging.INFO)
logging.basicConfig(format='%(asctime)s %(message)s')


KAPI= "7c88a4e043854ed6beeb8e06052616ef3d0fd01f"
fn='..//data//scraped_aqi_data.csv'

stations_url = "https://api.waqi.info/map/bounds/?token=" + KAPI + "&latlng=22.29,113.37,22.03,113.92"

rs = rqs.get(stations_url)
ds = json.loads(rs.text)


## records list of stations (toogle manually) 
if False:
    df = pd.DataFrame(columns=['lat', 'lon', 'uid', 'name'])
    for k in ds['data']:
        df=df.append(pd.DataFrame([[k['lat'], k['lon'], k['uid'], k['station']['name']]],columns=df.columns))
    df 
    df.to_csv('..//data//station_list.csv', index=False, encoding='utf-8')



df=pd.DataFrame(columns=['time', 'station','uid', 'aqi', 'co','h','no2','p','pm10','pm25','so2','t','w'])

"""
varnames = {
        pm25: "PM<sub>2.5</sub>",
        pm10: "PM<sub>10</sub>",
        o3: "Ozone",
        no2: "Nitrogen Dioxide",
        so2: "Sulphur Dioxide",
        co: "Carbon Monoxyde",
        t: "Temperature",
        w: "Wind",
        r: "Rain (precipitation)",
        h: "Relative Humidity",
        d: "Dew",
        p: "Atmostpheric Pressure",
      };
"""

for d in ds['data']:
    dico={}
    print ("getting data on "+ str(d['uid']))
    url = "https://api.waqi.info/feed/@"  + str(d['uid'])  + "/?token=" + KAPI
    print(url)
    rv = rqs.get(url)
    dv = json.loads(rv.text)
    
    dico['uid']=d['uid']
    dico['station']=d['station']['name']
    
    dico['aqi']=dv['data']['aqi']
    dico['time']= dv['data']['time']['s']
    
    for k in dv['data']['iaqi'].keys():
        dico[k] = dv['data']['iaqi'][k]['v']
        
    df = df.append(dico, ignore_index=True)
    

df.to_csv(fn, mode='a', header=False, index=False)  # record each url one after the other ... 
print("found "+str(len(df))+" rows added to file")
