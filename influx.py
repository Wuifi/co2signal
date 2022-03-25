#!/usr/bin/env python3

# import standard modules
import logging
import influxdb
from influxdb import DataFrameClient

def check_db_status(db_handler, db_name):
    """
    Check if InfluxDB handler has access to a database.
    If it doesn't exist try to create it.
    Parameters
    ----------
    db_handler: influxdb.InfluxDBClient
        InfluxDB handler object
    db_name: str
        Name of DB to check
    """
    try:
        dblist = db_handler.get_list_database()
    except Exception as e:
        logging.error('Problem connecting to database: %s', str(e))
        return
    if db_name not in [db['name'] for db in dblist]:
        logging.info(f'Database <{db_name}> not found, trying to create it')
        try:
            db_handler.create_database(db_name)
        except Exception as e:
            logging.error('Problem creating database: %s', str(e))
            return
    else:
        logging.debug(f'Influx Database <{db_name}> exists')
    logging.info(f'Connection to InfluxDB established and database <{db_name}> present')
    return

#influx dB client functions
def initinfluxclient(dbhost, dbport, dbuser, dbpasswd, dbname):
    try:
        influxclient = DataFrameClient(dbhost, dbport, dbuser, dbpasswd, dbname)
    except Exception as e:
        logging.error('Problem initialising influxDBclient: %s', str(e))
    return influxclient

