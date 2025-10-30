"""
MCP Client for Semantic Scholar.

Uses the `semanticscholar` library to search for academic papers.
"""
import json
import semanticscholar as sch
from semanticscholar.Paper import Paper # For type hinting
import requests
client = sch.SemanticScholar()

def search_papers(
    query: str,
    limit=10,
    offset=0,
    fields="title,corpusId,abstract,tldr,year,referenceCount,citationCount,citationStyles,externalIds",
) -> dict:
    # hash = get_url_hash(topic + str(limit) + str(offset) + fields)
    # data = None
    # if os.path.exists(f"{CACHE_DIR}/{hash}.json"):
    #     with open(f"{CACHE_DIR}/{hash}.json", "r", encoding="utf-8") as file:
    #         data = json.load(file)
    #         if "code" in data:
    #             if data["code"] == "429":
    #                 print("Rate limit exceeded")
    #                 data = None

    # if data is None:
    print(f"  [MCP Tool] search_papers called with query: '{query}', limit: {limit}")
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={query}&limit={limit}&offset={offset}&fields={fields}"
    print(url)
    response = requests.request("GET", url)
    data = response.json()
    if "code" in data:
        if data["code"] == "429":
            print("Rate limit exceeded")
            # data = None
            return data
    # with open(f"{CACHE_DIR}/{hash}.json", "w", encoding="utf-8") as file:
    #     json.dump(data, file, indent=4)
    return data

def search_papers_by_query(query: str, limit: int = 5) -> str:
    """
    Searches the Semantic Scholar database for academic papers
    and returns a JSON string of the results.
    """
    print(f"  [MCP Tool] search_papers called with query: '{query}', limit: {limit}")
    
    if not query:
        return json.dumps({"error": "Query parameter cannot be empty."})

    try:
        # Use the semanticscholar library to search
        # We specify fields_of_study=['Computer Science', 'Medicine', etc.] 
        # to get more relevant results, but for a general tool we can omit it.
        # We must request the fields we want, like 'abstract' and 'authors'.
        search_results: list[Paper] = client.search_paper(
            query, 
            limit=limit, 
            fields_of_study=[], # Empty list means search all fields
            fields=['title', 'abstract', 'authors', 'year', 'url']
        )

        if not search_results:
            return json.dumps({"message": "No papers found for this query."})

        # Process results into a simple list of dicts
        papers_list = []
        for paper in search_results:
            papers_list.append({
                "title": paper.title,
                "abstract": paper.abstract,
                "authors": [author['name'] for author in paper.authors],
                "year": paper.year,
                "url": paper.url
            })
        
        # Return as a JSON string
        return json.dumps(papers_list)

    except Exception as e:
        print(f"  [MCP Tool] Error in search_papers: {e}")
        return json.dumps({"error": f"An error occurred while searching: {str(e)}"})


semantic_scholar_tool_definitions = [
    # {                                           # <-- ADD THIS ENTIRE BLOCK
    #     "name": "search_papers",
    #     "description": "Searches the Semantic Scholar database for academic papers based on a query.",
    #     "parameters": {
    #         "type": "OBJECT",
    #         "properties": {
    #             "query": {
    #                 "type": "STRING",
    #                 "description": "The search query (e.g., 'machine learning models for climate change', 'impact of LLMs on education')."
    #             },
    #             "limit": {
    #                 "type": "INTEGER",
    #                 "description": "The maximum number of paper results to return. Defaults to 5."
    #             }
    #         },
    #         "required": ["query"]
    #     }
    # }
    {
        "name": "search_papers",
        "description": "Searches the Semantic Scholar database for academic papers based on a query.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "The query to search for (e.g., 'machine learning', 'climate change')."
                },
                "limit": {
                    "type": "INTEGER",
                    "description": "The maximum number of paper results to return. Defaults to 10."
                },
                "offset": {
                    "type": "INTEGER",
                    "description": "The number of results to skip before starting to collect the result set. Defaults to 0."
                },
                "fields": {
                    "type": "STRING",
                    "description": "Comma-separated list of fields to include in the results (e.g., 'title,abstract,year'). Defaults to 'title,corpusId,abstract,tldr,year,referenceCount,citationCount,citationStyles,externalIds'."
                }
            },
            "required": ["topic"]
        }
    }
]
if __name__ == '__main__':
    # Example for testing this module directly
    test_query = "large language models and healthcare"
    print(f"Testing Semantic Scholar search with query: '{test_query}'")
    results_json = search_papers(test_query, limit=3)
    print("Results:", results_json)
    # print(json.dumps(json.loads(results_json), indent=2))
