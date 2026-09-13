from scrapy_redis.spiders import RedisSpider
from scrapy import Request
from crawling.spiders.lxmlhtml import CustomLxmlLinkExtractor as LinkExtractor
from crawling.items import RawResponseItem


class LinkSpider(RedisSpider):
    """
    A spider that walks all links from the requested URL.
    This is the entrypoint for generic crawling.
    """
    name = "link"

    def parse(self, response):
        url = response.request.url
        self.logger.debug(f"crawled url {url}")

        cur_depth = response.meta.get("curdepth", 0)
        max_depth = response.meta.get("maxdepth", 0)
        allowed_domains = response.meta.get("allowed_domains", [])
        allow_regex = response.meta.get("allow_regex", [])
        deny_regex = response.meta.get("deny_regex", [])
        deny_exts = response.meta.get("deny_extensions", [])
        priority = response.meta.get("priority", 0)
        useragent = response.meta.get("useragent", None)

        # 1) capturer la réponse brute
        item = RawResponseItem(
            appid=response.meta.get("appid"),
            crawlid=response.meta.get("crawlid"),
            attrs=response.meta.get("attrs"),
            url=url,
            response_url=response.url,
            status_code=response.status,
            status_msg="OK",
            response_headers=self.reconstruct_headers(response),
            request_headers=response.request.headers,
            body=response.body,
            encoding=response.encoding,
            links=[],
        )

        # 2) si on n'a pas atteint la profondeur max, on continue à spider
        if cur_depth < max_depth:
            extractor = LinkExtractor(
                allow_domains=allowed_domains,
                allow=allow_regex,
                deny=deny_regex,
                deny_extensions=deny_exts,
            )
            for link in extractor.extract_links(response):
                link_url = link.url.strip()
                item["links"].append({"url": link_url, "text": link.text})
                req = Request(link_url, callback=self.parse, priority=priority - 10)
                req.meta.update({
                    "curdepth": cur_depth + 1,
                    "maxdepth": max_depth,
                    "allowed_domains": allowed_domains,
                    "allow_regex": allow_regex,
                    "deny_regex": deny_regex,
                    "deny_extensions": deny_exts,
                    "priority": priority - 10,
                    "appid": response.meta.get("appid"),
                    "crawlid": response.meta.get("crawlid"),
                    "attrs": response.meta.get("attrs"),
                    "useragent": useragent,
                })
                if useragent:
                    req.headers["User-Agent"] = useragent
                self.logger.debug(f"Trying to follow link '{req.url}'")
                yield req
        else:
            self.logger.debug(
                f"Max depth reached ({cur_depth}/{max_depth}), not spidering further."
            )

        # 3) on retourne toujours l'item de la réponse brute
        yield item
