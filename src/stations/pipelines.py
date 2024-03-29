# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import re
from itemadapter import ItemAdapter
from stations.exceptions import DropDuplicateStation, DropClosedStation, DropNotLandFixed, DropInvalidStation
from stations.items import OgimetStationItem


class OgimetClosedPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter["closed"]:
            raise DropClosedStation(f"Rejected {adapter[item.__class__.item_uid]}: closed")
        return item


class OgimetInvalidPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        m = re.match(r'^\d{5}$', adapter["wid"])
        if not m:
            raise DropInvalidStation(f"Bad Wid {adapter[item.__class__.item_uid]}")
        return item

class OscarWrongTypePipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if 'Land (fixed)' != adapter["type"]:
            raise DropNotLandFixed(f"Rejected {adapter[item.__class__.item_uid]}: type {adapter['type']}")
        return item


class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()
        self.seen = []

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
            item_uid = item.__class__.item_uid
        except AttributeError:
            item_uid = "uid"
        if adapter[item_uid] in self.ids_seen:
            duplicates = [i for i in self.seen if i[item_uid]==adapter[item_uid]]
            duplicates.append(adapter.asdict())
            notify = True
            if len(duplicates) == 2 and all((duplicates[0].get(k) == v for k, v in duplicates[1].items() if k != 'established')):
                notify = False
            if isinstance(item, OgimetStationItem):
                if all((o['closed'] == True for o in duplicates)):
                    notify = False
            if notify:
                print(f"---- Duplicates found (keeping first): \n{json.dumps(duplicates,sort_keys=True, indent=4)}")
            raise DropDuplicateStation(f"Duplicate station found: {adapter[item_uid]}")
        else:
            self.ids_seen.add(adapter[item_uid])
        self.seen.append(adapter.asdict())
        return item
