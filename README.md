
# scrapy-ogimet

Extract in csv/json/geojson format the ogimet website or the oscar website.

- **wid** WMO index
- **latitude** decimal format
- **longitude** decimal format
- **icao** ICAO code or '----' (only for ogimet)

## Interactive Map

https://flyingeek.github.io/scrapy-ogimet/

It is also possible to [draw a route](https://flyingeek.github.io/scrapy-ogimet/index.html#LFPG_LFPB_LFAT_07002_EGXT_03226_03155_03021_04283_BGAS_71665_CWFW_71691_CWST_CWHV_72614_KORF_74699_74783)

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
