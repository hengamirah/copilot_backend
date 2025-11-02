from fastapi import FastAPI, HTTPException
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.sessions import DatabaseSessionService
from src.core.dependencies import root_agent
from src.core.config import HOST, DBNAME, USER, PASSWORD, PORT
from ag_ui.core import RunAgentInput
from google.genai import types
import base64

from src.agents.services.custom_artifact_service import PostgresArtifactService
from typing import List, Dict, Optional

# Direct DSN string
artifact_service = PostgresArtifactService(
    dsn=f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}",
)

# from fastapi import Request, HTTPException
# from fastapi.responses import JSONResponse
# from starlette.middleware.base import BaseHTTPMiddleware
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# import jwt
# from typing import Optional

# SECRET_KEY = "your-secret-key-here"  # Store in environment variables
# ALGORITHM = "HS256"
# security = HTTPBearer()

# # ============== Token Verification ==============
# def verify_token(token: str) -> dict:
#     """
#     Verify JWT token and return payload.
#     This validates the token sent from your Next.js frontend via CopilotKit.
#     """
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token has expired")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid token")

# # ============== Authentication Middleware ==============
# class CopilotKitAuthMiddleware(BaseHTTPMiddleware):
#     """
#     Middleware to handle CopilotKit forwarded authentication.
    
#     CopilotKit automatically forwards the 'authorization' property from your
#     frontend's <CopilotKit properties={{authorization: token}}> as an
#     'Authorization: Bearer <token>' HTTP header to your backend.
#     """
#     async def dispatch(self, request: Request, call_next):
#         # Public routes that don't require authentication
#         public_paths = ["/docs", "/openapi.json", "/redoc", "/health", "/openapi"]
        
#         if request.url.path in public_paths:
#             return await call_next(request)
        
#         # Extract Authorization header (forwarded by CopilotKit)
#         auth_header = request.headers.get("Authorization")
        
#         if not auth_header:
#             return JSONResponse(
#                 status_code=401,
#                 content={
#                     "detail": "Authorization header missing",
#                     "hint": "Make sure you're passing authorization property in CopilotKit"
#                 }
#             )
        
#         # Verify Bearer token format
#         if not auth_header.startswith("Bearer "):
#             return JSONResponse(
#                 status_code=401,
#                 content={"detail": "Invalid authorization header. Expected 'Bearer <token>'"}
#             )
        
#         # Extract and verify the JWT token
#         token = auth_header.replace("Bearer ", "")
        
#         try:
#             # Verify the token
#             payload = verify_token(token)
            
#             # Store user information in request state
#             # This makes user data available in your agent logic if needed
#             request.state.user = payload
#             request.state.user_id = payload.get("sub") or payload.get("user_id")
            
#             # Log successful authentication (optional, for debugging)
#             print(f"✅ Authenticated user: {request.state.user_id}")
            
#             # Continue to the actual endpoint
#             response = await call_next(request)
#             return response
            
#         except HTTPException as e:
#             return JSONResponse(
#                 status_code=e.status_code,
#                 content={"detail": e.detail}
#             )
#         except Exception as e:
#             return JSONResponse(
#                 status_code=401,
#                 content={"detail": f"Authentication failed: {str(e)}"}
#             )
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_user_id_from_forwarded_props(run_input: RunAgentInput) -> str:
    """Extract user_id from forwarded_props with detailed logging."""
    
    logger.info(f"🔍 Incoming request - thread_id: {run_input.thread_id}")
    logger.info(f"🔍 Forwarded props: {run_input.forwarded_props}")
    
    # Extract userId
    user_id = None
    if run_input.forwarded_props and isinstance(run_input.forwarded_props, dict):
        user_id = run_input.forwarded_props.get("userId")
    
    if not user_id:
        user_id = "anonymous_user"
        logger.warning(f"⚠️ No userId provided, using: {user_id}")
    else:
        logger.info(f"✅ Using userId: {user_id}")
    
    return user_id

# Create ADK middleware agent instance
adk_root_agent = ADKAgent(
    adk_agent=root_agent,
    app_name="manufacturing_chat_app",
    session_service=DatabaseSessionService(
    db_url=f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}",
    
    # More robust connection pool settings
    pool_size=20,                    # Increase for concurrent users
    max_overflow=30,                 
    pool_timeout=60,                 # Give more time for connections
    pool_recycle=7200,               # Recycle every 2 hours instead of 1
    pool_pre_ping=True,              
    
    connect_args={
        "connect_timeout": 30,       # Increase timeout
        "options": "-c statement_timeout=60000",  # 60 second query timeout
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    } 
    ),
    artifact_service=artifact_service,
    user_id_extractor=extract_user_id_from_forwarded_props,
    session_timeout_seconds=None,
    use_in_memory_services=False
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Root Agent")

@app.get("/api/files", response_model=Dict)
async def list_resources(user_id: Optional[str] = None, session_id: Optional[str] = None, filename: Optional[str] = None):
    """
    Returns a list of metadata for all available artifacts/resources 
    managed by the PostgresArtifactService.
    
    """
    try:
        # Assuming list_all_resources is implemented on your custom service
        artifact_part: types.Part = await artifact_service.load_artifact(
            app_name="manufacturing_chat_app",
            user_id=user_id,
            session_id=session_id,
            filename=filename,
        ) 

        if not artifact_part:
            raise HTTPException(status_code=404, detail="Artifact not found")

        bytes_data = artifact_part.inline_data.data
        
        # 3. CRITICAL: Encode the bytes to Base64 (ASCII string)
        if isinstance(bytes_data, bytes):
            base64_encoded_data = base64.b64encode(bytes_data).decode('ascii')
        else:
            # Handle case where data might already be a string (though less likely here)
            base64_encoded_data = bytes_data 

        return {
            "mime_type": artifact_part.inline_data.mime_type,
            "data": base64_encoded_data # <-- 4. Return the Base64 string
        }
    
    except Exception as e:
        logger.error(f"Error retrieving resources via /api/files: {e}")
        # Return a 500 error on failure
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve resources from artifact service: {str(e)}"
        )
    
# app.add_middleware(CopilotKitAuthMiddleware)

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_root_agent, path="/api/agent")

if __name__ == "__main__":
    import uvicorn
    
    print(f"🚀 Starting server on http://localhost:{8000}")
    uvicorn.run(app, host="0.0.0.0", port=8000)

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