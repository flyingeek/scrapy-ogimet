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

NOT_CLOSED = '----'
MISSING_WIGOS = '0-0-0-MISSING'

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
    return None # also for '----'

def sort_primary_first(values):
    primary = [o['wigosStationIdentifier'] for o in values if o['primary'] == True]
    others = [o['wigosStationIdentifier'] for o in values if o['primary'] == False]
    return primary + others

class OgimetStationLoader(ItemLoader):
    default_output_processor = TakeFirst()
    icao_out = Compose(TakeFirst(), only_with_letters)
    latitude_out = Compose(TakeFirst(), convert)
    longitude_out = Compose(TakeFirst(), convert)
    wigos_out = Compose(TakeFirst(), lambda wigos : None if wigos == MISSING_WIGOS else wigos, stop_on_none=False)
    closed_out = Compose(TakeFirst(), lambda closed: False if closed == NOT_CLOSED else True)


class OgimetStationItem(scrapy.Item):
    item_uid = 'wid' # used by DuplicatesPipeline
    wigos = scrapy.Field()
    wid = scrapy.Field()
    icao = scrapy.Field()
    name = scrapy.Field()
    longitude = scrapy.Field()
    latitude = scrapy.Field()
    altitude = scrapy.Field(geojson_property=False)
    established = scrapy.Field(geojson_property=False)
    closed = scrapy.Field()
    country = scrapy.Field()


class OscarStationLoader(ItemLoader):
    default_output_processor = TakeFirst()
    operational_out = Compose(TakeFirst(), lambda operational: True if operational == "operational" else False)
    wigosStationIdentifiers_out = Compose(sort_primary_first)


class OscarStationItem(scrapy.Item):
    item_uid = 'wigos' # used by DuplicatesPipeline
    wigos = scrapy.Field()
    wid = scrapy.Field()
    name = scrapy.Field()
    country = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    operational = scrapy.Field()
    type = scrapy.Field(geojson_property=False)
    wigosStationIdentifiers = scrapy.Field()


# Filter Class used for csv/json only (not geojson)
class StationFilter:
    def __init__(self, feed_options):
        self.feed_options = feed_options

    def accepts(self, item):
        if isinstance(item, OscarStationItem):
            if "operational" in item and not item["operational"]:
                return False
        elif isinstance(item, OgimetStationItem):
            if "closed" in item and item["closed"]:
                return False
        return True
