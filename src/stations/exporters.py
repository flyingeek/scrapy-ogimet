from scrapy.exporters import JsonItemExporter
from scrapy.utils.python import to_bytes

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
        fields = item.fields
        export_properties = [k for k in fields if "geojson_property" not in fields[k] or fields[k]["geojson_property"]==False]
        properties = {k: item.get(k, None) for k in export_properties if k != 'latitude' and k != 'longitude'}
        itemdict = dict(
            type='Feature',
            geometry=dict(type='Point', coordinates=[item["longitude"], item["latitude"]]),
            properties=properties
        )
        data = to_bytes(self.encoder.encode(itemdict), self.encoding)
        data = b"\n".join([(self.spacer * 2) + line for line in data.splitlines()])
        self._add_comma_after_first()
        self.file.write(data)
