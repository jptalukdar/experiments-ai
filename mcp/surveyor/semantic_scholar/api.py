import requests

from surveyor.utils.urls import get_url_hash
import json
import os


def get_paper_info(
    doi: str,
    fields="title,corpusId,abstract,tldr,year,referenceCount,citationCount,citationStyles",
):
    if doi is None:
        raise ValueError("DOI is None")
    if doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")
    elif doi.startswith("https://"):
        doi = doi.replace("https://", "")
    url = f"https://api.semanticscholar.org/graph/v1/paper/{doi}?fields={fields}"
    response = requests.request("GET", url)
    return response.json()


CACHE_DIR = ".data/results/semantic"


def search_topic(
    topic: str,
    limit=60,
    offset=0,
    fields="title,corpusId,abstract,tldr,year,referenceCount,citationCount,citationStyles,externalIds",
):
    hash = get_url_hash(topic + str(limit) + str(offset) + fields)
    data = None
    if os.path.exists(f"{CACHE_DIR}/{hash}.json"):
        with open(f"{CACHE_DIR}/{hash}.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            if "code" in data:
                if data["code"] == "429":
                    print("Rate limit exceeded")
                    data = None

    if data is None:
        url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={topic}&limit={limit}&offset={offset}&fields={fields}"
        print(url)
        response = requests.request("GET", url)
        data = response.json()
        if "code" in data:
            if data["code"] == "429":
                print("Rate limit exceeded")
                data = None
                return data
        with open(f"{CACHE_DIR}/{hash}.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
    return data
