"""
This is the **REAL** Gemini API client.

It uses the `google-generativeai` Python SDK to make live calls to the API.
It loads the API key from a `.env` file for security.
"""
import os
import json
import google.genai as genai
from dotenv import load_dotenv
from google.genai import types

# Load environment variables from a .env file
load_dotenv()

# --- Load and Configure API Key ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please create a .env file and add it.")

# genai.configure(api_key=GEMINI_API_KEY)

# --- Initialize the Model ---
# Using Gemini 1.5 Flash as requested
# Set safety settings to be permissive for tool use, adjust as needed.
default_safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

client = genai.Client(
    api_key=GEMINI_API_KEY
)
model_name="gemini-2.5-flash"

# model = genai.GenerativeModel(
#     safety_settings=default_safety_settings
# )

def call_gemini_api(payload: dict) -> dict:
    """
    Calls the real Gemini API's generateContent method.

    The payload dict is constructed in `main.py` and matches the
    keyword arguments for `generate_content`.
    """
    print("  [REAL Gemini] API call initiated...")

    # Extract arguments from the payload
    contents = payload.get("contents")
    tools = payload.get("tools")
    tools = types.Tool(function_declarations=tools) if tools else None
    config = types.GenerateContentConfig(tools=[tools])
    try:
        # --- Make the actual API call ---
        # The SDK handles chat history (contents) and tool definitions
        if tools:
            response = client.models.generate_content(
                model=model_name, contents=contents, config=config)
        else:
            # Don't send `tools=None` if there are no tools (e.g., synthesis call)
            response = client.models.generate_content(model=model_name, contents=contents)

        # --- Convert Response to Dictionary ---
        # Your `main.py` expects a dictionary, not a SDK object.
        # `MessageToDict` converts the Google Protobuf object into a
        # dictionary that matches the JSON structure `main.py` was built for.
        # response_dict = MessageToDict(response._result)

        # response.
        print("  [REAL Gemini] API call successful. Response:")
        print("  " + json.dumps(response.model_dump_json(), indent=2).replace("\n", "\n  "))

        return response.model_dump()

    except Exception as e:
        print(f"  [REAL Gemini] API Error: {e}")
        # In a real app, you'd handle specific API errors (e.g., quota, auth)
        # For now, we'll re-raise to the FastAPI handler
        raise e

