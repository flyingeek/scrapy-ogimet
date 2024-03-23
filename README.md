
# scrapy-ogimet

Extraction des stations WMO connues par Ogimet.com. Pour chaque station on a:

- **wid** l'index WMO
- **icao** le nom icao ou '----'
- **latitude** au format décimal
- **longitude** au format décimal

## Installation

```sh
# create a virtual env and activate
python3 -m venv venv --no-site-packages
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

```sh
cd src
scrapy crawl ogimet -L INFO
# Les données sont extraites dans data/
```

Pour se limiter à un pays:

```sh
scrapy parse "https://ogimet.com/display_stations.php?lang=en&tipo=AND&estado=france&Send=Send" --spider=ogimet -c parse_stations  --cbkwargs='{"country": "france"}'
```
