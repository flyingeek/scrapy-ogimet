# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import re
from itemadapter import ItemAdapter
from stations.exceptions import DropDuplicateStation, DropClosedStation, DropNotLandFixed, DropInvalidStation, DropInvalidCoordinates
from stations.items import OgimetStationItem


class OgimetCoordinatesPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter.get('latitude'):
            latitude = self.convert(adapter['latitude'])
        if adapter.get('longitude'):
            longitude = self.convert(adapter['longitude'])
        if latitude is not None and longitude is not None:
            adapter['latitude'] = latitude
            adapter['longitude'] = longitude
            return item
        raise DropInvalidCoordinates(f"Invalid coordinates {adapter['longitude']} {adapter['latitude']}")

    def convert(self, dms):
        m = re.match(r"^(?P<degrees>\d{2})-(?P<minutes>\d{2})(?:-(?P<seconds>\d{2}))?(?P<orientation>N?|S)$", dms) # latitude with optional N
        if not m:
            m = re.match(r"^(?P<degrees>\d{2,3})-(?P<minutes>\d{2})(?:-(?P<seconds>\d{2}))?(?P<orientation>[EW])$", dms) # longitude
            if not m:
                return None
        sign = -1 if (m.group('orientation') or 'N') in ['S', 'W'] else 1
        cents = (float(m.group('minutes'))/60) + (float(m.group('seconds') or 0)/3600)
        return sign * (float(m.group('degrees')) + cents)


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
