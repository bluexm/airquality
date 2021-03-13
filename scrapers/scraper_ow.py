#!/usr/bin/env python
# coding: utf-8

import requests as rqs
import bs4 
import pandas as pd 
import json 
from imp import reload
import logging
reload(logging)
logging.basicConfig(filename='scrape_ow.log', level=logging.INFO, format='%(asctime)s %(message)s')

KAPI= "f092715753d229bc10273e794ecdfbad"
useOneCall=False

fn='..//data//scraped_ow_data' +  ("_weather" if useOneCall==False else "_onecall" ) + '.csv'

#values_url = "https://api.openweathermap.org/data/2.5/weather?q=Macau&appid="+KAPI
if useOneCall:
    ##request through onecall 
    urlbase = ["https://api.openweathermap.org/data/2.5/onecall?lat=","","&lon=","","&exclude=minutely,hourly,daily&appid=" + KAPI]
else:
    ## request through weather (less limitations)
    urlbase = ["http://api.openweathermap.org/data/2.5/weather?lat=","","&lon=","","&appid="+KAPI]

df=pd.DataFrame(columns=['station_uid','lon','lat','dt', 'sunrise','sunset','temp', 'feels_like','pressure','humidity',
                        'dew_point', 'uvi', 'clouds', 'visibility', 'wind_speed', 'wind_deg'])

def dico_from_onecall( ds):
    dico = {'lon':ds['coord']['lon'],'lat':ds['coord']['lat'], 'weather':ds['current']['weather'][0]['main']}
    ds['current'].pop('weather')
    for k in ds['current'].keys():
        dico[k] = ds['current'][k]
        #print(dico)    
    return dico

def dico_from_weather(ds):
        """   example of ds:
        {"coord":{"lon":139,"lat":35},
         "weather":[{"id":500,"main":"Rain","description":"light rain","icon":"10d"}],"base":"stations",
         "main":{"temp":288.71,"feels_like":287.73,"temp_min":288.71,"temp_max":288.71,"pressure":1001,"humidity":92},
         "visibility":3965,"wind":{"speed":3.34,"deg":222},"rain":{"1h":0.18},"clouds":{"all":94},"dt":1614662949,
         "sys":{"type":3,"id":2019346,"country":"JP","sunrise":1614633167,"sunset":1614674398},"timezone":32400,"id":1851632,"name":"Shuzenji","cod":200}
        """
       
        dico = {'lon':ds['coord']['lon'],'lat':ds['coord']['lat'], 
                'weather':ds['weather'][0]['main'], 'weather_desc':ds['weather'][0]['description']}
        for k in ds['main'].keys():
            dico[k] = ds['main'][k]
        dico['visibility']= ds['visibility']
        dico['wind_speed']= ds['wind']['speed']
        dico['wind_deg']= ds['wind']['deg']
        dico['rain']= ds['rain'] if 'rain' in list(ds.keys()) else ''
        dico['clouds']= ds['clouds']
        dico['dt']= ds['dt']
        dico['country']= ds['sys']['country'] if 'country' in list(ds['sys'].keys()) else ''
        dico['sunrise']= ds['sys']['sunrise']
        dico['sunset']= ds['sys']['sunset']
        
        return dico


# # Read stations measures 

logging.info('----> getting station weather ')

dfstations=pd.read_csv("..//data//station_list.csv",header=0)

for i,s in dfstations.iterrows():
    #print(s)
    urlbase[1],urlbase[3]=str(s.lat),str(s.lon)
    url= ''.join(urlbase)
    rs = rqs.get(url)
    ds = json.loads(rs.text)
    if useOneCall:
        dico = dico_from_onecall(ds)
    else:
        dico = dico_from_weather(ds)
    dico['station_uid']=s.uid
    df=df.append(dico, ignore_index=True) 


# # Read weather grid further from stations

#set grid 
latmax, lonmax= 31.266224, 122.238532  #shanghai
latmin, lonmin=  19.258517, 104.907299  #vietnam
nblats, nblons=20,20
steplat=(latmax-latmin)/nblats
steplon=(lonmax-lonmin)/nblons

dfgrid = pd.DataFrame([{'lat':latmin+i*steplat, 'lon':lonmin+j*steplon} for i in range(nblats) for j in range(nblons)])

logging.info('----> getting grid weather')

import time

for i,s in dfgrid.iterrows():
	#print(s)
	logging.info('reading {} {} '.format(str(s.lat),str(s.lon)))
	time.sleep(1)  # limitation 60 requests per minute : cf https://openweathermap.org/price
	urlbase[1],urlbase[3]=str(s.lat),str(s.lon)
	url= ''.join(urlbase)
	rs = rqs.get(url)
	ds = json.loads(rs.text)
    
	if useOneCall:
		dico = dico_from_onecall(ds)
	else:
		dico = dico_from_weather(ds)
	dico['station_uid']=0
    
	#print(dico)
	df=df.append(dico, ignore_index=True) 

# # save in csv

logging.info('writing data to file')
df.to_csv(fn, mode='a', header=False,index=False)  # record each url one after the other ... 
