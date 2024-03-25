
# scrapy-ogimet

Extract in csv/json/geojson format the ogimet website or the oscar website.

- **wid** WMO index
- **latitude** decimal format
- **longitude** decimal format
- **icao** ICAO code or '----' (only for ogimet)

## Interactive Map

https://flyingeek.github.io/scrapy-ogimet/

## Installation

```sh
# create a virtual env and activate
python3 -m venv venv --no-site-packages
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
source venv/bin/activate
cd src
scrapy crawl ogimet -L INFO
# Data are extracted in data
```
