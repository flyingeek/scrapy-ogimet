# This package will contain the spiders of your Scrapy project
#
# Please refer to the documentation for information on how to create and manage
# your spiders.
import json
class RoundingFloat(float):
    __repr__ = staticmethod(lambda x: format(x, '.6f'))

json.encoder.c_make_encoder = None
if hasattr(json.encoder, 'FLOAT_REPR'):
    # Python 2
    json.encoder.FLOAT_REPR = RoundingFloat.__repr__
else:
    # Python 3
    json.encoder.float = RoundingFloat

print(f"json.encoder.float patched in spiders.__init__.py to use format '.6f'")
