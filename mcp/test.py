import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

# Local imports
import schemas
from mcp_clients import registry as mcp_registry
from mcp_clients import google_calendar
from gemini_client import call_gemini_api
from google.genai import types
import asyncio



app = FastAPI(
    title="AI Agent Router",
    description="An API that uses Gemini to route prompts to MCP clients or answer directly."
)

@app.get("/", tags=["Status"])
async def read_root():
    """A simple health check endpoint."""
    return {"status": "AI Agent is running"}


# @app.post("/api/v1/chat", response_model=schemas.ChatResponse, tags=["AI"])
async def chat_endpoint(request: schemas.ChatRequest):
    """
    This is the main "router" endpoint.
    It takes a prompt and orchestrates the full "understand -> execute -> synthesize" flow.
    """
    print(f"\n--- New Request Received ---")
    print(f"Prompt: '{request.prompt}'")

    # 1. First call to Gemini: "Understand"
    # We send the prompt and the list of available tools.
    tools = mcp_registry.gemini_tool_definitions
    
    # Construct the payload for the first call
    # In a real app, you would also include chat history here
    payload_step1 = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": request.prompt}]
            }
        ],
        "tools": tools
    }

    print("\n[Step 1] Calling Gemini to 'Understand' (check for tool use)...")
    # This is our mock API call
    response_step1 = call_gemini_api(payload_step1)
    
    try:
        # Extract the first part of the response from the (mock) API
        response_part = response_step1["candidates"][0]["content"]["parts"][0]

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
                
                # Call the actual Python function with the arguments
                # The `**tool_args` syntax unpacks the dict into keyword arguments
                print(f"[Step 3] Executing MCP client: {tool_name}...")
                tool_result = tool_function(**tool_args)
                print(f"Tool Result: {tool_result}")

                # 4. Second call to Gemini: "Synthesize"
                # We send the *original prompt*, the *tool call request*, and the *tool's response*
                # back to Gemini so it can formulate a natural language answer.

                # This is the "history" we build for the second call
                function_response_part = types.Part.from_function_response(
                    name=tool_name,
                    response={"result": tool_result},
                )
                contents_step2 = [
                    # The original user prompt
                    {"role": "user", "parts": [{"text": request.prompt}]},
                    # The model's previous response (the function call)
                    {"role": "model", "parts": [response_part]},
                    # The result of *our* function execution
                    {
                        "role": "tool", # This role is crucial
                        "parts": [ 
                            function_response_part
                        ]
                    }
                ]
                
                payload_step2 = {"contents": contents_step2, "tools": tools}

                print("\n[Step 4] Calling Gemini to 'Synthesize' tool result...")
                response_step2 = call_gemini_api(payload_step2)
                
                final_text = response_step2["candidates"][0]["content"]["parts"][0]["text"]
                debug_info = {
                    "tool_called": tool_name,
                    "tool_args": tool_args,
                    "tool_result": tool_result
                }

            else:
                # Error: Gemini tried to call a tool we don't have
                print(f"[Error] Gemini requested unknown tool: {tool_name}")
                raise HTTPException(status_code=500, detail=f"AI requested unknown tool: {tool_name}")

        elif "text" in response_part:
            # 2. No tool needed. Gemini answered directly.
            print("[Step 2] No tool needed. Gemini answered directly.")
            final_text = response_part["text"]
            debug_info = {"tool_called": None}
        
        else:
            # This shouldn't happen with a valid API response
            raise HTTPException(status_code=500, detail="Invalid response from Gemini API")

        print(f"\nFinal Response: {final_text}")
        return schemas.ChatResponse(response=final_text, debug_info=debug_info)

    except (KeyError, IndexError, TypeError) as e:
        print(f"[Error] Failed to parse Gemini response: {e}")
        print(f"Response was: {response_step1}")
        raise HTTPException(status_code=500, detail=f"Error processing AI response: {e}")

if __name__ == "__main__":
    # uvicorn.run(app, host="0.0.0.0", port=8000)

    async def main():
        response = await chat_endpoint(schemas.ChatRequest(prompt="any events for 2025-10-27"))
        print(response)

    asyncio.run(main())
