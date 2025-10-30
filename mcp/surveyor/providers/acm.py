from surveyor.providers.provider import Provider


class ACMProvider(Provider):
    _provider = "ACM"

    def get_abstract(self):
        abstract = self.soup.find("section", id="abstract")
        if abstract:
            return abstract.text.strip()[8:]
        else:
            raise Exception("Abstract not found")

    def get_doi(self):
        doi = self.soup.find("div", class_="doi")
        if doi:
            return doi.text.strip()
        else:
            raise Exception("DOI not found")
