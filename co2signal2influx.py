#!/usr/bin/env python3

self_description = """
co2signal2influx is a tiny daemon written to fetch data from the co2signal-API and
writes it to an InfluxDB instance.
"""

# import standard modules
from argparse import ArgumentParser, RawDescriptionHelpFormatter
import configparser
import logging
import os
import signal
import time
from datetime import datetime

# import 3rd party modules
import requests
import ast
#import functions from files
from app_functions import *
from basic_functions import *
from influx import *

__version__ = "0.0.1"
__version_date__ = "2022-03-25"
__description__ = "co2signal2influx"
__license__ = "MIT"

# default vars
running = True
default_config = os.path.join(os.path.dirname(__file__), 'config.ini')
default_log_level = logging.INFO


def main():
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    # parse command line arguments
    args = parse_args()
    # set logging
    log_level = logging.DEBUG if args.verbose is True else default_log_level
    if args.daemon:
        # omit time stamp if run in daemon mode
        logging.basicConfig(level=log_level, format='%(levelname)s: %(message)s')
    else:
        logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s: %(message)s')
    # read config from ini file
    config = read_config(args.config_file)
    # set up influxdb handler
    influxdb_client = None
    try:
        dbhost=config.get('influxdb', 'host')
        dbport=config.getint('influxdb', 'port', fallback=8086)
        dbuser=config.get('influxdb', 'username')
        dbpasswd=config.get('influxdb', 'password')
        dbname=config.get('influxdb', 'database')
        protocol=config.get('influxdb', 'protocol')
        measurement_name=config.get('influxdb', 'measurement_name')

        influxdb_client=initinfluxclient(dbhost, dbport, dbuser, dbpasswd, dbname)
        

    except configparser.Error as e:
        logging.error("Config Error: %s", str(e))
        exit(1)
    except ValueError as e:
        logging.error("Config Error: %s", str(e))
        exit(1)
    # check influx db status
    check_db_status(influxdb_client, config.get('influxdb', 'database'))

    # create authenticated api client handler

    df=pd.DataFrame()
    api_request_interval = 60
    
    try:
        api_request_interval = config.getint('api', 'api_request_interval', fallback=3600)
        api_request_pause = config.getint('api', 'api_request_pause', fallback=1)
        token=config.get('api', 'token')
        countryCodes=ast.literal_eval(config.get('api', 'countryCodes')) #config parse as string, thus conversion into list is required

    except configparser.Error as e:
        logging.error("Config Error: %s", str(e))
        exit(1)
        
    API_request_counter=0
    # test connection
    try:
        df,API_request_counter=getdatafromAPIforzones(countryCodes,api_request_pause,token,API_request_counter)
        #print(df)  
        write2influx(influxdb_client,protocol,measurement_name,df)
        logging.info("Successfully connected to API and InfluxDB")
    except requests.exceptions.RequestException as e:
        if "401" in str(e):
            logging.error("Failed to connect to API '%s' using credentials. Check token!" %
                          config.get('api', 'token'))
        if "404" in str(e):
            logging.error("Failed to connect to API '%s' using credentials. Check url!" %
                          config.get('api', 'url'))
        else:
            logging.error(str(e))
            print(df)
        exit(1)

    logging.info("Starting main loop - wait until next API-Request '%s' seconds",api_request_interval)
    duration=0
    
    while running:
        
        start = int(datetime.utcnow().timestamp() * 1000)  
        logging.info("Starting API requests")
        time.sleep(api_request_interval) # wait, otherwise Exception 429, 'Limitation: maximum number of requests per second exceeded']
        df_response, API_request_counter=getdatafromAPIforzones(countryCodes,api_request_pause,token,API_request_counter)
        write2influx(influxdb_client,protocol,measurement_name,df_response)
        duration = int(datetime.utcnow().timestamp() * 1000) - start
        logging.info("Duration of requesting API: %0.3fs" % (duration / 1000)) 
        # just sleep for interval seconds - last run duration
        for _ in range(0, int(((api_request_interval * 1000) - duration) / 100)):
            if running is False:
                break
            time.sleep(0.0965)
            
            
if __name__ == "__main__":
    main()
