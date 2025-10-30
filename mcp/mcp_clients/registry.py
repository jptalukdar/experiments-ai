"""
This file acts as the central registry for all MCP clients (tools).

It does two things:
1.  Defines the JSON schema for the tools, which we will send to Gemini.
2.  Maps the tool names to the actual Python functions that implement them.
"""
from . import google_calendar
from . import semantic_scholar
from . import google_scholar
# from . import date_tools

# 1. Define the tool implementations
# This map tells our `main.py` which function to call for a given tool name.
tool_implementations = {
    "fetch_calendar_events": google_calendar.fetch_calendar_events,
    "add_calendar_event": google_calendar.add_calendar_event,
    # "search_papers": semantic_scholar.search_topic,
    "web_search_query_by_page_id": google_scholar.web_search_query_by_page_id
    # Add new MCP clients here, e.g.:
    # "get_user_location": user_service.get_location,
}


# 2. Define the tool schemas for Gemini
# This is the "menu" we give to the AI so it knows what tools it can use.
# This should be a flat list of function declaration objects.
# The Python SDK will automatically wrap this in a Tool object.
gemini_tool_definitions = []
gemini_tool_definitions.extend(google_calendar.google_calendar_tool_definitions)
# gemini_tool_definitions.extend(semantic_scholar.semantic_scholar_tool_definitions)
gemini_tool_definitions.extend(google_scholar.gemini_google_gse_schema)
    


