import logging
import os
import time
from collections import defaultdict

import requests
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, ValidationError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ollama Gemma Secure Auth API")
security = HTTPBearer()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
VALID_TOKEN = os.getenv("AUTH_TOKEN", "SECRET_TOKEN")
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", "50"))

user_requests = defaultdict(lambda: {"count": 0, "reset_time": time.time()})

print(f"Starting Ollama Gemma Secure Auth API on port {os.getenv('PORT', '8000')}")
print(f"Ollama URL: {OLLAMA_URL}")
print(f"Rate Limit: {RATE_LIMIT_PER_HOUR} requests per hour")

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    model: str = Field(default="gemma:2b", min_length=1, max_length=100, pattern="^[a-zA-Z0-9_:-]+$")
    

def verify_token_and_rate_limit(
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if credentials.credentials != VALID_TOKEN:
        logger.warning(f"SECURITY_ALERT: Invalid token attempt from {request.client.host}")
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    client_ip = request.client.host
    current_time = time.time()

    if current_time > user_requests[client_ip]["reset_time"]:
        user_requests[client_ip] = {
            "count": 0,
            "reset_time": current_time + 3600
        }

    if user_requests[client_ip]["count"] >= RATE_LIMIT_PER_HOUR:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded: {RATE_LIMIT_PER_HOUR}/hour")

    user_requests[client_ip]["count"] += 1
    return True


@app.post("/validate")
async def validate_token(request: Request):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(status_code=401, detail="Missing Authorization header")

        if not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid Authorization format")

        token = auth_header.split(" ")[1]

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        verify_token_and_rate_limit(request, credentials)
        
        print(f"TOKEN_VALIDATION: IP={request.client.host}")

        logger.info(f"AUTH_SUCCESS: Token validated for {request.client.host}")
        return {"status": "authorized"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AUTH_ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail="Authentication error") from e


@app.get("/")
async def root():
    return {"message": "Ollama gemma Secure Auth API", "version": "2.0-secure"}


@app.post("/chat")
async def chat(
        request: ChatRequest,
        http_request: Request,
        authorized: bool = Depends(verify_token_and_rate_limit)
):
    print(f"CHAT_REQUEST: IP={http_request.client.host},"
                f"Model={request.model},"
                f"MsgLen={len(request.message)}")

    try:
        models_response = requests.get(f"{OLLAMA_URL}/api/tags")
        if models_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Model")

        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": request.model,
                "prompt": request.message,
                "stream": False,
                "options": {
                    "num_ctx": 2048,  # Reduce context window (default is 4096)
                    "num_thread": 4   # Reduce CPU threads
                }
            }
        )

        if response.status_code == 200:
            logger.info("CHAT_SUCCESS: Request completed")
            return response.json()
        else:
            raise HTTPException(status_code=500, detail="Ollama API error")

    except requests.exceptions.ConnectionError:
        logger.error("CHAT_ERROR: Ollama connection failed")
        raise HTTPException(status_code=503, detail="Ollama service unavailable")
    except Exception as e:
        logger.error(f"CHAT_ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")
    
    
@app.get("/models")
async def get_models(request: Request, authorized: bool = Depends(verify_token_and_rate_limit)):
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hata: {str(e)}")


@app.get("/health")
async def health():
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags")
        status = "healthy" if response.status_code == 200 else "unhealthy"
        return {"status": status, "ollama_connection": OLLAMA_URL}
    except Exception as e:
        return {"status": "unhealthy", "ollama_connection": "disconnected", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
