import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import json

# Local imports
import mcp_clients.registry as mcp_registry
from mcp_clients import google_calendar
from gemini_client import call_gemini_api
from google.genai import types

# --- Pydantic Schemas ---
# We define the schemas here to include the new history fields.
# In a real app, you would modify your 'schemas.py' file.

class ChatRequest(BaseModel):
    """
    The request model for the chat endpoint.
    It now includes a 'history' field to maintain conversation state.
    """
    prompt: str
    # The 'history' is a list of all previous 'content' objects from the Gemini API
    # The client is responsible for sending this back on each turn.
    history: List[Dict[str, Any]] = Field(default_factory=list)

class ChatResponse(BaseModel):
    """
    The response model for the chat endpoint.
    It returns the text response and the full, updated conversation history.
    """
    response: str
    # The 'updated_history' is the complete history (including the latest turn)
    # The client should store this and send it as 'history' in the next request.
    updated_history: List[Dict[str, Any]]
    debug_info: Dict[str, Any]


# --- FastAPI App ---

app = FastAPI(
    title="AI Agent Router (with Session)",
    description="An API that uses Gemini to route prompts to MCP clients or answer directly, now with conversational memory."
)

@app.get("/", tags=["Status"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "AI Agent is running"}


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["AI"])
async def chat_endpoint(request: ChatRequest):
    """
    This is the main "router" endpoint with session management.
    It takes a new prompt and the previous conversation history,
    orchestrates the "understand -> execute -> synthesize" flow,
    and returns the response plus the updated history.
    """
    print(f"\n--- New Request Received ---")
    print(f"Prompt: '{request.prompt}'")
    print(f"Received history with {len(request.history)} items.")

    # 1. First call to Gemini: "Understand"
    # We send the *full history* plus the *new prompt*.
    tools = mcp_registry.gemini_tool_definitions
    
    # This is the new user message
    new_user_content = {"role": "user", "parts": [{"text": request.prompt}]}
    
    # This is the history we'll use for the *first* call
    # It's the old history + the new prompt
    contents_step1 = request.history + [new_user_content]
    
    payload_step1 = {
        "contents": contents_step1,
        "tools": tools
    }

    print("\n[Step 1] Calling Gemini to 'Understand' (check for tool use)...")
    # This is our mock API call
    response_step1 = call_gemini_api(payload_step1)
    
    try:
        # Extract the model's response (this is a full 'content' object)
        # e.g., {"role": "model", "parts": [{"function_call": ...}]}
        model_content_step1 = response_step1["candidates"][0]["content"]
        response_part = model_content_step1["parts"][0] # Just the first part for checking

        if "function_call" in response_part:
            # 2. Gemini wants to call a tool
            print("[Step 2] Gemini requested a tool call.")
            fc = response_part["function_call"]
            tool_name = fc["name"]
            tool_args = fc.get("args", {})
            
            print(f"Tool to call: {tool_name}")
            print(f"Arguments: {tool_args}")

            # 3. Execute the tool (call the MCP client)
            if tool_name in mcp_registry.tool_implementations:
                tool_function = mcp_registry.tool_implementations[tool_name]
                
                print(f"[Step 3] Executing MCP client: {tool_name}...")
                tool_result = tool_function(**tool_args)
                print(f"Tool Result: {tool_result}")

                # 4. Second call to Gemini: "Synthesize"
                # We build the *next* step of the history, which includes
                # the model's function call AND the tool's result.

                function_response_part = types.Part.from_function_response(
                    name=tool_name,
                    response={"result": tool_result},
                )
                
                # This is the content object for the tool's response
                tool_content = {
                    "role": "tool", # This role is crucial
                    "parts": [function_response_part]
                }

                # This is the full history *so far*
                # old_history + user_prompt + model_function_call + tool_result
                contents_step2 = contents_step1 + [model_content_step1, tool_content]
                
                payload_step2 = {"contents": contents_step2, "tools": tools}

                print("\n[Step 4] Calling Gemini to 'Synthesize' tool result...")
                response_step2 = call_gemini_api(payload_step2)
                
                # Get the final model response (text)
                model_content_step2 = response_step2["candidates"][0]["content"]
                final_text = model_content_step2["parts"][0]["text"]
                
                # This is the *complete* history for this turn
                updated_history = contents_step2 + [model_content_step2]

                debug_info = {
                    "tool_called": tool_name,
                    "tool_args": tool_args,
                    "tool_result": tool_result,
                    "history_items_in": len(request.history),
                    "history_items_out": len(updated_history)
                }
                
                print(f"\nFinal Response: {final_text}")
                return ChatResponse(
                    response=final_text,
                    updated_history=updated_history,
                    debug_info=debug_info
                )

            else:
                # Error: Gemini tried to call a tool we don't have
                print(f"[Error] Gemini requested unknown tool: {tool_name}")
                raise HTTPException(status_code=500, detail=f"AI requested unknown tool: {tool_name}")

        elif "text" in response_part:
            # 2. No tool needed. Gemini answered directly.
            print("[Step 2] No tool needed. Gemini answered directly.")
            final_text = response_part["text"]
            
            # The full history is just the history + user prompt + model's text response
            updated_history = contents_step1 + [model_content_step1]
            
            debug_info = {
                "tool_called": None,
                "history_items_in": len(request.history),
                "history_items_out": len(updated_history)
            }
            
            print(f"\nFinal Response: {final_text}")
            return ChatResponse(
                response=final_text,
                updated_history=updated_history,
                debug_info=debug_info
            )
        
        else:
            # This shouldn't happen with a valid API response
            raise HTTPException(status_code=500, detail="Invalid response from Gemini API")

    except (KeyError, IndexError, TypeError) as e:
        print(f"[Error] Failed to parse Gemini response: {e}")
        print(f"Response was: {response_step1}")
        raise HTTPException(status_code=500, detail=f"Error processing AI response: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
