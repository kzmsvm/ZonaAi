from html.parser import HTMLParser
from urllib.request import urlopen
from zona.plugins import PluginBase


class _TitleParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        if tag.lower() == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


class Plugin(PluginBase):
    """Simple web scraper plugin using standard library only."""

    def run(self, args: str, context: dict) -> dict:
        url = args.strip()
        if not url:
            return {"result": "No URL provided"}
        with urlopen(url) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        parser = _TitleParser()
        parser.feed(html)
        return {"result": parser.title.strip() or "No title found"}

    def get_metadata(self) -> dict:
        return {
            "name": "web_scraper",
            "description": "Fetches webpage title",
            "version": "1.0",
        }
