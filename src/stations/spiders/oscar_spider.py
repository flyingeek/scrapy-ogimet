import logging
import scrapy
import re
from stations.items import OscarStationItem, OscarStationLoader

class OscarSpider(scrapy.Spider):
    name = "oscar"

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        print(OscarStationItem.fields)
        settings.set("DOWNLOAD_DELAY", 0, priority="spider")
        settings.set("FEED_EXPORT_FIELDS", ['wigos', 'wid', 'longitude', 'latitude'], priority="spider")
        settings.set("ITEM_PIPELINES",{
            "stations.pipelines.OscarWrongTypePipeline": 300,
            "stations.pipelines.DuplicatesPipeline": 400
            }, priority="spider")


    def start_requests(self):
        urls = [
            "https://gist.github.com/flyingeek/54caad59410a1f4641d480473ec824c3/raw/oscar_wmo_stations.json"
            # "https://oscar.wmo.int/surface/rest/api/search/station?facilityType=landFixed&programAffiliation=GOSGeneral,RBON,GBON,RBSN,RBSNp,RBSNs,RBSNsp,RBSNst,RBSNt,ANTON,ANTONt&variable=216&variable=224&variable=227&variable=256&variable=310&variable=12000",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_stations)

    def parse_stations(self, response):
        logging.info(f"Parsing oscar stations")
        for item in response.json()["stationSearchResults"]:
            wid = None
            m = re.search(r"^0-20000-0-(\d{5})$", item["wigosId"])
            if m:
                wid = m.group(1)
            loader = OscarStationLoader(OscarStationItem())
            loader.add_value('wigos', item["wigosId"])
            loader.add_value('wid', wid)
            loader.add_value('name', item["name"])
            loader.add_value('country', item["territory"])
            loader.add_value('latitude', item["latitude"])
            loader.add_value('longitude', item["longitude"])
            loader.add_value('operational', item["stationStatusCode"])
            loader.add_value('type', item["stationTypeName"])
            loader.add_value('wigosStationIdentifiers', item["wigosStationIdentifiers"])
            yield loader.load_item()
