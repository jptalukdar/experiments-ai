from surveyor.providers.provider import Provider
from urllib.parse import urlparse

get_path = lambda url: urlparse(url).path


class ArxivProvider(Provider):
    _provider = "Arxiv"

    # def download_pdf(self) -> str:
    def __init__(self, url: str, cache: bool = True, fetch_mode: str = "selenium"):
        urltype = get_path(url).split("/")[1]
        print(urltype)
        if urltype == "pdf":
            document_id = url.split("/")[-1]
            url = f"https://arxiv.org/abs/{document_id}"
            print(url)
        if urltype == "html":
            document_id = url.split("/")[-1]
            url = f"https://arxiv.org/abs/{document_id}"
            print(url)
        super().__init__(url, cache, fetch_mode)

    def get_abstract(self) -> str:
        abstract = self.soup.find("blockquote", class_="abstract mathjax")
        if abstract:
            return abstract.text.strip()[9:]
        else:
            raise Exception("Abstract not found")

    def get_doi(self) -> str:
        doi = self.soup.find("a", id="arxiv-doi-link")
        if doi:
            return doi.text.strip()
        else:
            print("DOI Missing: ", self.url)
            raise Exception("DOI not found")
