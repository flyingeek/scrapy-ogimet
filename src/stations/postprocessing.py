"""
Extension for processing data before they are exported to feeds.
"""
import io
import logging
from typing import Any, BinaryIO, Dict
import pandas as pd


class DropDuplicates:
    """
    Drop duplicates using panda.

    We do not use a Pipeline since we want to get rid of all duplicate record.
    Using a Pipeline only allows to keep the first duplicate.

    Accepted ``feed_options`` parameters:

    - `keep: "first"|"last"|False`
    if False all duplicates are removed, it is the default
    """

    def __init__(self, file: BinaryIO, feed_options: Dict[str, Any]) -> None:
        self.file = file
        self.feed_options = feed_options
        self.keep = self.feed_options.get("keep", False)
        self.buffer = io.StringIO()

    def write(self, data: bytes) -> int:
        format = self.feed_options['format']
        if format in ['json', 'csv']:
            self.buffer.write(data.decode('UTF-8'))
            return self.buffer.tell()
        return self.file.write(data)

    def close(self) -> None:
        format = self.feed_options['format']
        if format in ['json', 'csv']:
            self.buffer.seek(0)
            df = pd.read_json(self.buffer) if format == 'json' else pd.read_csv(self.buffer)
            subset = ['wigos'] # oscar
            if 'icao' in df.columns:
                subset = ['wid'] # ogimet
            df = df.drop_duplicates(subset=subset, keep=self.keep)
            if format == 'json':
                df.to_json(self.file, orient="records", indent=self.feed_options.get('indent', None), double_precision=6)
            else:
                df.to_csv(self.file, index=False, float_format='%.6f')
            logging.info(f"DropDuplicates stored {format} feed ({len(df)} items) in: {self.file.name}")
            del df
        self.buffer.close()
        self.file.close()
