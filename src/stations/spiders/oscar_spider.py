import logging
import scrapy
import re
from stations.items import OscarStationItem

class OscarSpider(scrapy.Spider):
    name = "oscar"

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        settings.set("DOWNLOAD_DELAY", 0, priority="spider")
        settings.set("FEED_EXPORT_FIELDS", ['wid', 'longitude', 'latitude'], priority="spider")
        settings.set("ITEM_PIPELINES",{
            "stations.pipelines.InvalidOscarInputPipeline": 300,
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
            m = re.search(r"-0-(\d{5})$", item["wigosId"])
            if m:
                wid = m.group(1)
            yield OscarStationItem(
                wigos=item["wigosId"],
                wid=wid,
                name=item["name"],
                country=item["territory"],
                latitude=item["latitude"],
                longitude=item["longitude"],
                operational=item["stationStatusCode"],
                type=item["stationTypeName"],
            )
