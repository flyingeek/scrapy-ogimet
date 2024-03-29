
# scrapy-ogimet

Extract in csv/json/geojson format the ogimet website or the oscar website.

In the CSV/JSON file, duplicates are dropped in postprocessing,
we do not even keep the first one.

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
# ogimet for France only
scrapy crawl ogimet -L INFO -a country=france
# ogimet all countries
scrapy crawl ogimet -L INFO
# oscar can only fetch all countries
scrapy crawl oscar -L INFO
```

### Cache

Cache is enabled by default

```sh
# Disable cache temporary from command line
scrapy crawl ogimet -L INFO -s HTTPCACHE_ENABLED=False
# erase the cache
rm -rf .scrapy/httpcache/ogimet
rm -rf .scrapy/httpcache/oscar

```

### Output

Since the interactive map runs on github pages from the docs folder,
data are extracted in the docs/data subfolder as csv, json and geojson
