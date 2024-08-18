import logging
from scrapy.exceptions import DropItem

class PoliteDropItem(DropItem):
    polite_loglevel = logging.DEBUG
    def __init__(self, *a, **kw):
        self.polite_loglevel = kw.pop("polite_log_level", self.polite_loglevel)
        super().__init__(*a)

class DropInvalidCoordinates(PoliteDropItem):
    pass

class DropInvalidStation(PoliteDropItem):
    pass

class DropDuplicateStation(PoliteDropItem):
    pass

class DropClosedStation(PoliteDropItem):
    pass

class DropNotOperational(PoliteDropItem):
    pass

class DropNotLandFixed(PoliteDropItem):
    pass
