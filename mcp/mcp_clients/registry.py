"""
This file acts as the central registry for all MCP clients (tools).

It does two things:
1.  Defines the JSON schema for the tools, which we will send to Gemini.
2.  Maps the tool names to the actual Python functions that implement them.
"""
from . import google_calendar
# from . import date_tools

# 1. Define the tool implementations
# This map tells our `main.py` which function to call for a given tool name.
tool_implementations = {
    "fetch_calendar_events": google_calendar.fetch_calendar_events,
    "add_calendar_event": google_calendar.add_calendar_event,
    # "get_today_date": date_tools.get_today_date,
    # "get_relative_date": date_tools.get_relative_date,
    # Add new MCP clients here, e.g.:
    # "get_user_location": user_service.get_location,
}


# 2. Define the tool schemas for Gemini
# This is the "menu" we give to the AI so it knows what tools it can use.
# This should be a flat list of function declaration objects.
# The Python SDK will automatically wrap this in a Tool object.
gemini_tool_definitions = [
    {
        "name": "fetch_calendar_events",
        "description": "Get a list of Google Calendar events for a specific date.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "date": {
                    "type": "STRING",
                    "description": "The date to fetch events for, in YYYY-MM-DD format."
                }
            },
            "required": ["date"]
        }
    },
    {
        "name": "add_calendar_event",
        "description": "Add a new event to the Google Calendar.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "summary": {
                    "type": "STRING",
                    "description": "The title or summary of the event (e.g., 'Dentist Appointment')."
                },
                "date": {
                    "type": "STRING",
                    "description": "The date of the event, in YYYY-MM-DD format."
                },
                "start_time": {
                    "type": "STRING",
                    "description": "The event start time in 24-hour HH:MM format (e.g., '14:30')."
                },
                "end_time": {
                    "type": "STRING",
                    "description": "The event end time in 24-hour HH:MM format (e.g., '15:30')."
                }
            },
            "required": ["summary", "date", "start_time", "end_time"]
        }
    },
    # {
    #     "name": "get_today_date",
    #     "description": "Get today's date in YYYY-MM-DD format.",
    #     "parameters": {
    #         "type": "OBJECT",
    #         "properties": {},
    #         "required": []
    #     }
    # },
    # {
    #     "name": "get_relative_date",
    #     "description": "Get the date for a relative day (e.g., today, tomorrow, yesterday) in YYYY-MM-DD format.",
    #     "parameters": {
    #         "type": "OBJECT",
    #         "properties": {
    #             "relative_day": {
    #                 "type": "STRING",
    #                 "description": "The relative day to get the date for. Valid values: 'today', 'tomorrow', 'yesterday'."
    #             }
    #         },
    #         "required": ["relative_day"]
    #     }
    # },
    # Add new tool schemas here
]

