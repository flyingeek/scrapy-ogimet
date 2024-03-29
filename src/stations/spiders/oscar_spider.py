import logging
import scrapy
import re
from stations.items import OscarStationItem, OscarStationLoader

class OscarSpider(scrapy.Spider):
    name = "oscar"
    legacy = None  # dict of legacy station index

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        print(OscarStationItem.fields)
        settings.set("DOWNLOAD_DELAY", 0, priority="spider")
        settings.set("FEED_EXPORT_FIELDS", ['wigos', 'wid', 'longitude', 'latitude', 'operational', "wigosStationIdentifiers"], priority="spider")
        settings.set("ITEM_PIPELINES",{
            "stations.pipelines.OscarWrongTypePipeline": 300,
            "stations.pipelines.DuplicatesPipeline": 400
            }, priority="spider")


    def start_requests(self):
        yield scrapy.Request(url="https://gist.github.com/flyingeek/54caad59410a1f4641d480473ec824c3/raw/vola_legacy_report.txt", callback=self.parse_legacy_index)
        if not hasattr(self, 'url') or self.url == 'gist':
            url = "https://gist.github.com/flyingeek/54caad59410a1f4641d480473ec824c3/raw/oscar_wmo_stations.json"
        elif self.url == 'live':
            url = "https://oscar.wmo.int/surface/rest/api/search/station?facilityType=landFixed&programAffiliation=GOSGeneral,RBON,GBON,RBSN,RBSNp,RBSNs,RBSNsp,RBSNst,RBSNt,ANTON,ANTONt&variable=216&variable=224&variable=227&variable=256&variable=310&variable=12000"
            url = "https://oscar.wmo.int/surface/rest/api/search/station?facilityType=landFixed&stationClass=synopLand&programAffiliation=GOSGeneral,RBON,GBON,RBSN,RBSNp,RBSNs,RBSNsp,RBSNst,RBSNt,ANTON,ANTONt"
            url = "https://oscar.wmo.int/surface/rest/api/search/station?facilityType=landFixed&programAffiliation=GOSGeneral,RBON,GBON,RBSN,RBSNp,RBSNs,RBSNsp,RBSNst,RBSNt,ANTON,ANTONt"
        else:
            url = self.url
        yield scrapy.Request(url=url, callback=self.parse_stations)

    def parse_legacy_index(self, response):
        self.legacy = dict()
        for line in response.text.splitlines():
            m = re.search(r"\s(0-\S+)\s+(\d+)\s+(\d+)\s", line)
            if m:
                wigosId = m.group(1)
                legacyID = m.group(2)
                # legacySub = m.group(3)
                self.legacy[wigosId] = legacyID
        logging.info(f"found {len(self.legacy)} legacy WMO (Vol.A)")

    def getWid(self, wigos_id):
        wid = self.legacy.get(wigos_id, None)
        if not wid:
            m = re.search(r"^0-2000[0-1]-0-(\d{5})$",wigos_id)
            if m:
                wid = m.group(1)
                logging.info(f"added legacy {wid} for {wigos_id}")
        return wid

    def parse_stations(self, response):
        logging.info(f"Parsing oscar stations")
        for item in response.json()["stationSearchResults"]:
            loader = OscarStationLoader(OscarStationItem())
            wid = None
            if "wigosStationIdentifiers" in item:
                loader.add_value('wigosStationIdentifiers', item["wigosStationIdentifiers"])
                for wigos in item["wigosStationIdentifiers"]:
                    wid = self.getWid(wigos["wigosStationIdentifier"])
                    if wid:
                        break
            elif "wigosId" in item:
                wid = self.getWid(item["wigosId"])
            else:
                continue

            loader.add_value('wigos', item["wigosId"])
            loader.add_value('wid', wid)
            loader.add_value('name', item["name"])
            loader.add_value('country', item["territory"])
            loader.add_value('latitude', item["latitude"])
            loader.add_value('longitude', item["longitude"])
            loader.add_value('operational', item["stationStatusCode"])
            loader.add_value('type', item["stationTypeName"])
            yield loader.load_item()
