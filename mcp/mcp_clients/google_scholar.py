import enum
import urllib.parse
import requests
from bs4 import BeautifulSoup
import os
# from surveyor.providers.provider import Provider
from surveyor.providers import *
from surveyor.providers import provider

RESULTS_DIR = ".data/results/gcse"
if not os.path.exists(RESULTS_DIR):
    os.makedirs(RESULTS_DIR)


def get_url(query, page, px_cse="3487676ad0ae64afa", sort=""):
    query = urllib.parse.quote(query)
    return f"https://cse.google.com/cse?cx={px_cse}#gsc.tab=0&gsc.q={query}&gsc.sort={sort}&gsc.page={page}"


def get_results(query, page=1, sort=""):
    url = get_url(query, page, sort=sort)
    prv = Provider(url, cache=False, fetch_mode="selenium")
    print("Processing", url, prv.get_url_hash())

    soup = prv.soup
    res = soup.find_all("div", class_="gsc-webResult gsc-result")
    result = []
    for r in res:
        title = r.find("a", class_="gs-title").text
        link = r.find("a", class_="gs-title")["href"]
        snippet = r.find("div", class_="gs-bidi-start-align gs-snippet").text
        # print(title, link, snippet)
        result.append({"title": title, "link": link, "snippet": snippet})
    return result, prv.get_url_hash()


def fetch_provider_details(result):
    json_info = []

    # for i, r in enumerate(result):
    #     print(f"Fetching {i+1}/{len(result)}")
    #     try:
    #         p = load_provider(r["link"])
    #         info = p.get_info()
    #         json_info.append(info)
    #     except Exception as e:
    #         print(e, r["link"])
    return result


def web_search_query_by_page_id(query, page_num=1, sort="date"):
    result, urlhash = get_results(query, page_num, sort)
    json_info = {
        "query": query,
        "page": page_num,
        "results": fetch_provider_details(result),
    }
    # json_info = fetch_provider_details(result)
    with open(f"{RESULTS_DIR}/{urlhash}.json", "w", encoding="utf-8") as file:
        json.dump(json_info, file, indent=4)
    
    return json_info



gemini_google_gse_schema= [
    {
     "name": "web_search_query_by_page_id",
     "description": "Performs a web search using Google Custom Search Engine (CSE) and returns results for the specified page number.",
     "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query string"},
            "page_num": {"type": "integer", "description": "Page number to fetch", "minimum": 1},
            "sort": {"type": "string", "description": "Sort order for results", "enum": [ "relevance" ,"date"]},
        },
        "required": ["query"]
        }
    
    }
    
    ]


if __name__ == "__main__":
    web_search_query_by_page_id("Cross-organizational identity management", page_num=1, sort="date")
# result, urlhash = get_results("Cross-organizational identity management")
