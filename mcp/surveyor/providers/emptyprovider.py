from surveyor.providers.provider import Provider


class EmptyProvider(Provider):
    _provider = "Empty"

    def get_abstract(self) -> str:
        return "Abstract not found"
