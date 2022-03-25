#!/usr/bin/python3

import logging
import os
import requests
import json

import time
from datetime import datetime

import pandas as pd



default_log_level = logging.INFO

def getCO2zones(myapitoken):
    try:
        url="https://api.electricitymap.org/v3/zones"
        resp=requests.get(url)
        #import requests
        #from requests.structures import CaseInsensitiveDict

        #url ="https://api.electricitymap.org/v3/zones" 
        #headers = CaseInsensitiveDict()
        #headers["auth-token"] = myapitoken

        #resp = requests.get(url, headers=headers)
        if "401" in str(resp.status_code):
            logging.error("Failed to connect to API '%s' using credentials. Check token!" %myapitoken)
    except requests.exceptions.RequestException as e:
        if "401" in str(e):
            logging.error("Failed to connect to API '%s' using credentials. Check token!" %myapitoken)
                          #config.get('gridradar', 'token'))
        if "404" in str(e):
            logging.error("Failed to connect to API '%s' using credentials. Check url!" %url)
                          #config.get('gridradar', 'url'))
        if "429" in str(e):
            logging.error("Failed to connect to API -- Too many Requests!")
        else:
            logging.error(str(e))
    except Exception as e:
        logging.error(str(e))
    return resp

def getCO2dataforzone(token,countryCode):
    try:
        import requests
        from requests.structures import CaseInsensitiveDict

        baseurl = "https://api.co2signal.com/v1/latest"
        request='?countryCode='+countryCode
        url=baseurl+request
        headers = CaseInsensitiveDict()
        headers["auth-token"] = token

        resp = requests.get(url, headers=headers)
        
    except requests.exceptions.RequestException as e:
        if "401" in str(e):
            logging.error("Failed to connect to API '%s' using credentials. Check token!" %token)
                          #config.get('gridradar', 'token'))
        if "404" in str(e):
            logging.error("Failed to connect to API '%s' using credentials. Check url!" %url)
                          #config.get('gridradar', 'url'))
        if "429" in str(e):
            logging.error("Failed to connect to API -- Too many Requests!")
        else:
            logging.error(str(e))
    except Exception as e:
        logging.error(str(e))
    return resp



def parseAPIresponse2df(response):
    df=pd.DataFrame()
    df.loc[0,'API_status_code']=response.status_code
    #print(response.status_code)
    try:
        response_dict=response.json()
        #print(response_dict['status'])
        #print(response_dict['countryCode'])
        #print(response_dict['data'])
        #print(response_dict['units'])

        data_dict=response_dict['data']
        for key, value in data_dict.items():
            #print(key, '->', value)
            df.loc[0,key]=value
        
        df.loc[0,'countryCode']=response_dict['countryCode']    
        df.loc[0,'status']=response_dict['status']
             
    except Exception as e:
        logging.error(str(e))
    return df

def getdatafromAPIforzones(countryCodes,api_request_pause,token,API_request_counter):
    
    df=pd.DataFrame()
  
    for countryCode in countryCodes:
        #print(countryCode)
        logging.info("API request for zone: %s", countryCode)
        resp=getCO2dataforzone(token,countryCode)
        API_request_counter=API_request_counter+1
        df_new=parseAPIresponse2df(resp)
        df_new.loc[0,'API_request_counter']=API_request_counter
        df=pd.concat([df, df_new], ignore_index=True)
        time.sleep(api_request_pause) #

    df['datetime']=pd.to_datetime(df['datetime'])#, format='%Y-%m%d', errors='ignore')
    df=df.set_index('datetime')

    return df, API_request_counter

def write2influx(influxdb_client,protocol,measurement,df):
    try:
        # Write data to measurement.
        #client.write_points(df,"SchoolData",tags=fixtags,tag_columns=datatags,protocol=protocol)
        for idx in df.index:
            dfonedataset=df[df.index==idx]#print(df.loc[idx, :])
            #print(dfonedataset)
            fixtags={'countryCode': dfonedataset.countryCode[0]}
            influxdb_client.write_points(dfonedataset,measurement,tags=fixtags,protocol=protocol)
    except Exception as e:
        logging.error('Problem writing data to influxDB: %s', str(e))
    return

