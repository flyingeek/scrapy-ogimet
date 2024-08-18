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

OGIMET_EMPTY = '----'
MISSING_WIGOS = '0-0-0-MISSING'

def sort_primary_first(values):
    primary = [o['wigosStationIdentifier'] for o in values if o['primary'] == True]
    others = [o['wigosStationIdentifier'] for o in values if o['primary'] == False]
    return ";".join(primary + others)  # use or ';' to be compatible with comma delimited csv

class OgimetStationLoader(ItemLoader):
    default_output_processor = TakeFirst()
    icao_out = Compose(TakeFirst(), lambda icao: None if icao == OGIMET_EMPTY else icao)
    latitude_out = TakeFirst()
    longitude_out = TakeFirst()
    wigos_out = Compose(TakeFirst(), lambda wigos : None if wigos == MISSING_WIGOS else wigos)
    closed_out = Compose(TakeFirst(), lambda closed: False if closed == OGIMET_EMPTY else True)


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
    wid_out = Compose(TakeFirst(), str)
    wigosStationIdentifiers_out = Compose(sort_primary_first)


class OscarStationItem(scrapy.Item):
    item_uid = 'wigos' # used by DuplicatesPipeline
    wigos = scrapy.Field()
    wid = scrapy.Field()
    wid_guess = scrapy.Field()
    name = scrapy.Field()
    country = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    operational = scrapy.Field()
    type = scrapy.Field(geojson_property=False)
    wigosStationIdentifiers = scrapy.Field()
