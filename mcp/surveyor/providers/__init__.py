# mypy: disable-error-code="return-value"
from surveyor.providers.sciencedirect import *
from surveyor.providers.arxiv import *
from surveyor.providers.ieeexplore import *
from surveyor.providers.provider import *
from surveyor.providers.emptyprovider import *
from surveyor.providers.springer import *
from surveyor.providers.multi_providers import *
from surveyor.providers.acm import *
from urllib.parse import urlparse


def get_domain(url) -> str:
    """Extract the domain from the URL."""

    parsed_url = urlparse(url)
    return parsed_url.netloc


def get_provider(url: str) -> Provider:
    domain = get_domain(url)
    match domain:
        case "www.sciencedirect.com":
            return ScienceDirectProvider
        case "arxiv.org":
            return ArxivProvider
        case "www.arxiv.org":
            return ArxivProvider
        case "ieeexplore.ieee.org":
            return IEEEXplore
        case "link.springer.com":
            return SpringerProvider
        case "www.mdpi.com":
            return MDPI
        case "onlinelibrary.wiley.com":
            return Wiley
        case "ietresearch.onlinelibrary.wiley.com":
            return Wiley
        case "www.frontiersin.org":
            return Frontiers
        case "dl.acm.org":
            return ACMProvider
        case "www.techrxiv.org":
            return TechRxiv
        case "www.cambridge.org":
            return Cambridge
        case "journals.sagepub.com":
            return SagePub
        case "oro.open.ac.uk":
            return OpenUniversity
        case _:
            return EmptyProvider


def load_provider(url) -> Provider:
    return get_provider(url)(url)
