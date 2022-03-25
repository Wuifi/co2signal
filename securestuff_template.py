#API config
myapitoken="tkoen"
countryCodes=['DE','BE']#,'FR','IT']
api_request_pause=1 #sec, otherwise "429 Too Many Requests" fault appears
api_request_interval=1*3600 #every hour. data is only updated on an hourly basis
#influxDB config
measurement="co2signal"
dbhost = 'ip'
dbport = 8086
dbuser = 'user'
dbpasswd = 'password'
dbname = 'test'
protocol = 'line'