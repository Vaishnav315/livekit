import os
import uvicorn
import datetime  
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit import api

app = FastAPI()

# 1. Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. LiveKit Configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://defensecommand-0hpjg8is.livekit.cloud")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "APIHvSUQcBAaEDQ")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "PzybOIstZODQiLB3hW4m2ZQsCDfE5CKrel69XWwfadIB")

@app.get("/")
def root():
    return {"status": "LiveKit Token Server Online"}

@app.get("/token")
async def get_token(identity: str, room_name: str = "war-room"):
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise HTTPException(status_code=500, detail="Server misconfiguration: Missing LiveKit Keys")

    # 3. Define Permissions
    grant = api.VideoGrants(
        room_join=True, 
        room=room_name,
        can_publish=True, 
        can_subscribe=True
    )
    
    # 4. Create the Token
    # FIX: Use datetime.timedelta for the TTL
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
        .with_identity(identity) \
        .with_grants(grant) \
        .with_name(identity) \
        .with_ttl(datetime.timedelta(hours=24)) 
        
    jwt_token = token.to_jwt()
    
    print(f"🔑 Generated token for user: {identity}")
    
    return {
        "token": jwt_token, 
        "url": LIVEKIT_URL
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
