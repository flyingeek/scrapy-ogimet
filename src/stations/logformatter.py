from scrapy import logformatter

class PoliteLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        if hasattr(exception, "polite_loglevel"):
            return {
                'level': exception.polite_loglevel,
                'msg': "Dropped: %(exception)s",
                'args': {
                    'exception': exception,
                    'item': item,
                }
            }
        return super().dropped(item, exception, response, spider)
