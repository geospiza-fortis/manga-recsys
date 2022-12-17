import pandas as pd
import scrapy

BASE_URI = "https://api.mangadex.org"


class MangaSpider(scrapy.Spider):
    name = "mangaspider"

    # 5 requests per second rate limit
    custom_settings = {
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 5,
        "DOWNLOAD_DELAY": 1 / 5,
        "LOG_LEVEL": "WARNING",
        "RANDOMIZE_DOWNLOAD_DELAY": False,
    }

    def __init__(self, path, limit=None, **kwargs):
        df = pd.read_csv(path)
        if limit:
            df = df.head(int(limit))
        self.start_urls = df._id.apply(lambda x: f"{BASE_URI}/chapter/{x}").tolist()
        super().__init__(**kwargs)

    def parse(self, response):
        yield response.json()["data"]
