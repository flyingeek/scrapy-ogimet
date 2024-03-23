import logging
from scrapy.exceptions import DropItem


class DropInvalidStation(DropItem):
    polite_loglevel = logging.DEBUG

class DropDuplicateStation(DropItem):
    polite_loglevel = logging.DEBUG

class DropClosedStation(DropItem):
    polite_loglevel = logging.DEBUG

class DropNotOperational(DropItem):
    polite_loglevel = logging.DEBUG

class DropNotLandFixed(DropItem):
    polite_loglevel = logging.DEBUG
