from surveyor.providers.provider import AbstractClassProvider


class Wiley(AbstractClassProvider):
    _provider = "Wiley"

    def get_abstract(self):
        return super().get_abstract_by_class("article-section__content en main")

    def get_doi(self):
        s = self.soup.find("a", class_="epub-doi")
        if s:
            return s["href"]
        else:
            raise Exception("DOI not found")


class Frontiers(AbstractClassProvider):
    _provider = "Frontiers"

    def __init__(self, url, cache=True, fetch_mode="selenium"):
        if url.endswith("pdf"):
            url = url.replace("pdf", "full")
        super().__init__(url, cache, fetch_mode)

    def get_abstract(self):
        return super().get_abstract_by_class("JournalAbstract")

    def get_doi(self):
        s = self.soup.find("a", class_="ArticleLayoutHeader__info__doi")
        if s:
            return s["href"]
        else:
            raise Exception("DOI not found")


class MDPI(AbstractClassProvider):
    _provider = "MDPI"

    def get_doi(self):
        s = self.soup.find("div", class_="bib-identity")
        if s:
            return s.find("a")["href"]
        else:
            raise Exception("DOI not found")

    def get_abstract(self):
        return super().get_abstract_by_element("section", "html-abstract")


class TechRxiv(AbstractClassProvider):
    _provider = "TechRxiv"

    def __init__(self, url, cache=True, fetch_mode="selenium"):
        if url.find("/pdf/") != -1:
            url = url.replace("/pdf/", "/full/")
        super().__init__(url, cache, fetch_mode)

    def get_abstract(self):
        return super().get_abstract_by_class("article-paragraph preview-abstract")

    def get_doi(self):
        s = self.soup.find("span", class_="publication-status__citation-doi")
        if s:
            return s.find("a")["href"]
        else:
            raise Exception("DOI not found")


class Cambridge(AbstractClassProvider):
    _provider = "Cambridge"

    def get_abstract(self):
        return super().get_abstract_by_class("abstract-content")

    def get_doi(self):
        s = self.soup.find("div", class_="doi-data")
        if s:
            doi = s.find("a")
            if doi:
                return doi["href"]
            else:
                return s.text
        else:
            raise Exception("DOI not found")


class SagePub(AbstractClassProvider):
    _provider = "SagePub"

    def get_abstract(self):
        return super().get_abstract_by_element("section", "abstract-content")

    def get_doi(self):
        s = self.soup.find("div", class_="doi")
        if s:
            doi = s.find("a")
            if doi:
                return doi["href"]
            else:
                return s.text
        else:
            raise Exception("DOI not found")


class OpenUniversity(AbstractClassProvider):
    _provider = "OpenUniversity"

    def get_abstract(self):
        return super().get_abstract_by_element("p", "abstract_body")

    def get_doi(self):
        s = self.soup.find("p", class_="doi")
        if s:
            doi = s.find("a")
            if doi:
                return doi["href"]
            else:
                return s.text
        else:
            raise Exception("DOI not found")
