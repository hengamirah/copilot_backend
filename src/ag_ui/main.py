from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

from src.core.dependencies import root_agent

# Create ADK middleware agent instance
adk_root_agent = ADKAgent(
    adk_agent=root_agent,
    app_name="demo_app",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Root Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_root_agent, path="/api/agent")

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Check for Google API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ Warning: GOOGLE_API_KEY not set!")
        print("Set it with: export GOOGLE_API_KEY='your-key-here'")
    
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on http://localhost:{port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)


# {
#   "threadId": "thread_123",
#   "runId": "run_456",
#   "state": {},
#   "messages": [
#     {
#       "id": "msg_1",
#       "role": "user",
#       "content": "Hello, how can you help me?"
#     }
#   ],
#   "tools": [],
#   "context": [],
#   "forwardedProps": {}
# }