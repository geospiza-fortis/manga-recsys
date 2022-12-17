import pandas as pd
import scrapy
import tqdm

BASE_URI = "https://api.mangadex.org"


class GroupSpider(scrapy.Spider):
    name = "groupspider"

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
        df = pd.read_parquet(path)
        groups = pd.Series(
            df.relationships.apply(lambda x: x["scanlation_group"]).unique()
        )
        self.limit = 100
        if limit:
            groups = groups.head(int(limit))

        self.start_urls = (
            groups.apply(lambda x: f"{BASE_URI}/group/{x}").unique().tolist()
        )
        self.progress = tqdm.tqdm(total=len(self.start_urls))
        super().__init__(**kwargs)

    def parse(self, response):
        return response.json()["data"]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(GroupSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.item_scraped, signal=scrapy.signals.item_scraped)
        return spider

    async def item_scraped(self, item):
        self.progress.update(1)
