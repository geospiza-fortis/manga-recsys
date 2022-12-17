import pandas as pd
import scrapy

BASE_URI = "https://api.mangadex.org"


class ChapterSpider(scrapy.Spider):
    name = "chapterspider"

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
        self.limit = 100
        if limit:
            df = df.head(int(limit))
        self.start_urls = df._id.apply(
            lambda x: f"{BASE_URI}/chapter?manga={x}&limit={self.limit}"
        ).tolist()
        super().__init__(**kwargs)

    def parse(self, response):
        resp_json = response.json()
        for item in resp_json["data"]:
            yield item

        # also get the response url to check if it has a offset parameter, if it
        # does, then we can break early since we only spawn new requests from
        # the start_urls
        if "offset" in response.url:
            return None

        # get the total number of chapters, and yield new responses as necessary
        total = resp_json["total"]
        if total > self.limit:
            for offset in range(self.limit, total, self.limit):
                yield scrapy.Request(
                    f"{response.url}&offset={offset}", callback=self.parse
                )
