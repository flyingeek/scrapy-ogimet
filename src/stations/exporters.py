from scrapy.exporters import JsonItemExporter
from scrapy.utils.python import to_bytes
from stations.items import ICAO_DEFAULT

class GeoJsonItemExporter(JsonItemExporter):

    def __init__(self, file, **kwargs):
        super().__init__(file, **kwargs)
        if self.indent is not None and self.indent > 0:
            self.spacer = b' ' * self.indent

    def start_exporting(self):
        self.file.write(b'{')
        self._beautify_newline()
        self.file.write((self.spacer * 1) + b'"type": "FeatureCollection",')
        self._beautify_newline()
        self.file.write((self.spacer * 1) + b'"features": [')
        self._beautify_newline()

    def finish_exporting(self):
        self._beautify_newline()
        self.file.write((self.spacer * 1) + b']')
        self._beautify_newline()
        self.file.write(b'}')

    def export_item(self, item):
        properties = dict(id=item["wid"])
        if ("icao" in item and item["icao"] != ICAO_DEFAULT):
            properties["icao"] = item["icao"]
        if ("name" in item):
            properties["name"] = item["name"]
        if ("country" in item):
            properties["country"] = item["country"]
        itemdict = dict(
            type='Feature',
            geometry=dict(type='Point', coordinates=[item["longitude"], item["latitude"]]),
            properties=properties
        )
        data = to_bytes(self.encoder.encode(itemdict), self.encoding)
        data = b"\n".join([(self.spacer * 2) + line for line in data.splitlines()])
        self._add_comma_after_first()
        self.file.write(data)
