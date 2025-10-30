from surveyor.providers.provider import Provider


class SpringerProvider(Provider):
    def __init__(self, url: str, cache: bool = True, fetch_mode: str = "selenium"):
        if url.endswith(".pdf"):
            url = url.replace(".pdf", "").replace("/content/pdf/", "/article/")
        super().__init__(url, cache, fetch_mode)

    def get_abstract(self) -> str:
        abstract = self.soup.find("div", id="Abs1-content")
        if abstract:
            return abstract.text.strip()
        else:
            print(f"Abstract not found in {self.url}")
            return "Abstract not found"

    def get_doi(self) -> str:
        s = self.soup.find("meta", {"name": "citation_doi"})
        if s:
            return f'https://{s["content"]}'
        else:
            raise Exception("DOI not found")
