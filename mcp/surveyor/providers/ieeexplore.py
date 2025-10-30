from surveyor.providers.provider import Provider


class IEEEXplore(Provider):
    _provider = "IEEEXplore"

    def __init__(self, url: str, cache: bool = True, fetch_mode: str = "selenium"):
        if url.endswith(".pdf"):
            document_id = url.split("/")[-1].replace(".pdf", "").lstrip("0")
            url = f"https://ieeexplore.ieee.org/document/{document_id}"
        super().__init__(url, cache, fetch_mode)

    def get_abstract(self) -> str:
        abstract = self.soup.find("div", class_="abstract-text")
        if abstract:
            return abstract.text.strip()[9:]
        else:
            print(f"Abstract not found in {self.url}")
            return "Abstract not found"

    def fetch_html(self, url):
        return self.fetch_using_selenium(url)

    def get_title(self) -> str:
        title = self.soup.find("meta", property="og:title")
        if title:
            return title["content"]
        else:
            print(f"Title not found in {self.url}")
            return "Title not found"

    @staticmethod
    def download_url(title, url):
        return Provider.download_using_chrome(title, url)

    def get_doi(self) -> str:
        doi = self.soup.find("div", class_="stats-document-abstract-doi")
        if doi:
            return doi.find("a")["href"]
        else:
            print(f"DOI not found in {self.url}")
            raise Exception(f"DOI not found in {self.url}")
