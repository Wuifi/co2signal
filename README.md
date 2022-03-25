# co2signal2influx

co2signal2influx is a tiny daemon written to fetch data from the [co2signal.com](https://co2signal.com/)-API and
writes it to an InfluxDB instance.


# Requirements
* python3.6 or newer
* influxdb
* 

# Setup
* here we assume we install in ```/opt```



## Run with Docker
```
git clone <this_repo_url>
cd co2signal2influx
```

Copy the config from the [example](config_template.ini) to ```config.ini``` and edit
the settings.

Now you should be able to build and run the image with following commands
```
docker build -t co2signal2influx .
docker run -d -v /PATH/TO/config.ini:/app/config.ini --name co2signal2influx co2signal2influx
```

You can alternatively use the provided [docker-compose.yml](docker-compose.yml):
```
docker-compose up -d
```
If you're running the influxdb in a docker on the same host you need to add `--link` to the run command.

### Example:
* starting the influx container
```
docker run --name=influxdb -d -p 8086:8086 influxdb
```
* set influxdb host in `config.ini` to `influxdb`
* run docker container
```
docker run --link influxdb -d -v /PATH/TO/config.ini:/app/config.ini --name co2signal2influx co2signal2influx
```


# Grafana

Use ```grafana_dashboard_co2signal2influx.json``` to import this dashboard.


![Grafana Dashboard](grafana_dashboard.jpg)

# Configure more attributes

check here to find a overview of more attributes which probaly could be added
https://service.gridradar.net/index.php?menu=doc

# License
>You can check out the full license [here](LICENSE.txt)

This project is licensed under the terms of the **MIT** license.
