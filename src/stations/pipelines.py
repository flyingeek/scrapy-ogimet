# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import re
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from stations.exceptions import DropInvalidStation, DropDuplicateStation, DropClosedStation, DropNotOperational, DropNotLandFixed

def checkIds(wigos, wid):
    if not re.match(r"^0-20000-0-\d{5}$", wigos):
        raise DropInvalidStation(f"Rejected wigos {wigos}")
    if not re.match(r"^\d{5}$", wid):
        raise DropInvalidStation(f"Rejected wmo index {wid}")

class InvalidOgimetInputPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        checkIds(adapter["wigos"], adapter["wid"])
        if '----' != adapter["closed"]:
            raise DropClosedStation(f"Rejected {adapter["wid"]}: closed on {adapter['closed']}")
        return item

class InvalidOscarInputPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        checkIds(adapter["wigos"], adapter["wid"])
        if 'operational' != adapter["operational"]:
            raise DropNotOperational(f"Rejected {adapter["wid"]}: status {adapter['operational']}")
        if 'Land (fixed)' != adapter["type"]:
            raise DropNotLandFixed(f"Rejected {adapter["wid"]}: type {adapter['type']}")
        return item


class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter["wid"] in self.ids_seen:
            raise DropDuplicateStation(f"Duplicate station found: {adapter["wid"]}")
        self.ids_seen.add(adapter["wid"])
        return item


# class InvalidLatLonPipeline:
#     def process_item(self, item, spider):
#         adapter = ItemAdapter(item)
#         if not re.match(r"^[-\d.]+$", adapter["latitude"]):
#             raise DropItem(f"Invalid latitude {adapter["latitude"]}")
#         if not re.match(r"^[-\d.]+$", adapter["longitude"]):
#             raise DropItem(f"Invalid longitude {adapter["longitude"]}")
#         return item
