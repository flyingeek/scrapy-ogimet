import logging
import scrapy
from stations.items import OgimetStationItem, OgimetStationLoader
import unicodedata

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

class StationsSpider(scrapy.Spider):
    name = "ogimet"

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        settings.set("DOWNLOAD_DELAY", 10, priority="spider")
        settings.set("FEED_EXPORT_FIELDS", ['wid', 'icao', 'wigos', 'longitude', 'latitude'], priority="spider")
        settings.set("ITEM_PIPELINES",{
            "stations.pipelines.OgimetInvalidPipeline": 310,
            "stations.pipelines.DuplicatesPipeline": 400
        }, priority="spider")

    def start_requests(self):
        if hasattr(self, 'country'):
            yield self.countryFormRequest(self.country)
        else:
            yield scrapy.Request(url="https://ogimet.com/usynops.phtml.en", callback=self.parse_countries)

    def countryFormRequest(self, country):
        return scrapy.FormRequest(
                url="https://ogimet.com/display_stations.php",
                method="GET",
                formdata={"lang": "en", "tipo": "AND", "estado": strip_accents(country).lower(), "Send": "Send"},
                callback=self.parse_stations,
                cb_kwargs={"country": strip_accents(country)},
            )

    def parse_countries(self, response):
        countries = response.css("select[name=estado] option::text").getall()
        for country in countries:
            yield self.countryFormRequest(country)

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
            item = loader.load_item()
            yield item
