import logging
import scrapy
from stations.items import OgimetStationItem, OgimetStationLoader

class StationsSpider(scrapy.Spider):
    name = "ogimet"

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        settings.set("DOWNLOAD_DELAY", 10, priority="spider")
        settings.set("FEED_EXPORT_FIELDS", ['wid', 'icao', 'longitude', 'latitude'], priority="spider")
        settings.set("ITEM_PIPELINES",{
            "stations.pipelines.InvalidOgimetInputPipeline": 300,
            "stations.pipelines.DuplicatesPipeline": 400
        }, priority="spider")

    def start_requests(self):
        urls = [
            "https://ogimet.com/usynops.phtml.en",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_countries)

    def parse_countries(self, response):
        countries = response.css("select[name=estado] option::text").getall()
        # countries = ['spain']
        for country in countries:
            yield scrapy.FormRequest(
                url="https://ogimet.com/display_stations.php",
                method="GET",
                formdata={"lang": "en", "tipo": "AND", "estado": country.lower(), "Send": "Send"},
                callback=self.parse_stations,
                cb_kwargs={"country": country},
            )

    def parse_stations(self, response, country):
        logging.info(f"Parsing ogimet stations for {country}")
        for row in response.xpath('//table[@class="border_black"]/tr')[1:]:
            loader = OgimetStationLoader(OgimetStationItem(), selector=row)
            loader.add_xpath("wigos", 'td[1]//text()')
            loader.add_xpath("wid", 'td[2]//text()')
            loader.add_xpath("icao", 'td[3]//text()')
            loader.add_xpath("name", 'td[4]//text()')
            loader.add_xpath("country", 'td[5]//text()')
            loader.add_xpath("latitude", 'td[6]//text()')
            loader.add_xpath("longitude", 'td[7]//text()')
            loader.add_xpath("altitude", 'td[8]//text()')
            loader.add_xpath("established", 'td[9]//text()')
            loader.add_xpath("closed", 'td[10]//text()')
            yield loader.load_item()
