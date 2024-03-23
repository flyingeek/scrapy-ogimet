# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy.exceptions import DropItem
from itemloaders.processors import TakeFirst, Compose
from decimal import *

ICAO_DEFAULT = '----'

def convert(dms):
    m = re.match(r"^(\d{2})-(\d{2})(?:-(\d{2}))?(N?|S)$", dms) # latitude with optional N
    if not m:
        m = re.match(r"^(\d{2,3})-(\d{2})(?:-(\d{2}))?([EW])$", dms) # longitude
        if not m:
            raise DropItem(f"Invalid latitude {dms}")
    direction = m.group(4) if m.group(4) else 'N'
    sign = -1 if direction in ['S', 'W'] else 1
    deg = float(m.group(1))
    minutes = float(m.group(2))
    seconds = float(m.group(3)) if m.group(3) else 0
    cents = (minutes/60) + (seconds/3600)
    return sign * (deg + cents)

def only_with_letters(icao):
    m = re.match(r"^[A-Z]{4}$", icao)
    if m:
        return icao
    return ICAO_DEFAULT


class OgimetStationLoader(ItemLoader):
    default_output_processor = TakeFirst()
    icao_out = Compose(TakeFirst(), only_with_letters)
    latitude_out = Compose(TakeFirst(), convert)
    longitude_out = Compose(TakeFirst(), convert)

class OgimetStationItem(scrapy.Item):
    wigos = scrapy.Field()
    wid = scrapy.Field()
    icao = scrapy.Field()
    name = scrapy.Field()
    longitude = scrapy.Field()
    latitude = scrapy.Field()
    altitude = scrapy.Field()
    established = scrapy.Field()
    closed = scrapy.Field()
    country = scrapy.Field()

class OscarStationItem(scrapy.Item):
    wigos = scrapy.Field()
    wid = scrapy.Field()
    name = scrapy.Field()
    country = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    operational = scrapy.Field()
    type = scrapy.Field()
