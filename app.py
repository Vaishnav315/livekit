import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from livekit import api

app = FastAPI()

# 1. Enable CORS (Allows your Mobile App to talk to this server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, change this to your app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. LiveKit Configuration
# It tries to get keys from Render's Environment Variables first.
# If not found, it falls back to the hardcoded keys you provided (for safety/testing).
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://defensecommand-0hpjg8is.livekit.cloud")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "APIHvSUQcBAaEDQ")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "PzybOIstZODQiLB3hW4m2ZQsCDfE5CKrel69XWwfadIB")

@app.get("/")
def root():
    return {"status": "LiveKit Token Server Online"}

@app.get("/token")
async def get_token(identity: str, room_name: str = "war-room"):
    """
    Generates a JWT Token for LiveKit.
    Usage: GET /token?identity=Scout-1
    """
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise HTTPException(status_code=500, detail="Server misconfiguration: Missing LiveKit Keys")

    # 3. Define Permissions
    # This grant allows the user to Publish (send video) and Subscribe (watch video)
    grant = api.VideoGrant(
        room_join=True, 
        room=room_name,
        can_publish=True, 
        can_subscribe=True
    )
    
    # 4. Create the Token
    token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
        .with_identity(identity) \
        .with_grants(grant) \
        .with_name(identity) \
        .with_ttl(24 * 60 * 60) # Token valid for 24 hours
        
    jwt_token = token.to_jwt()
    
    print(f"🔑 Generated token for user: {identity}")
    
    # 5. Return to App
    return {
        "token": jwt_token, 
        "url": LIVEKIT_URL
    }

if __name__ == "__main__":
    # Render expects the app to run on port 10000 or $PORT
    port = int(os.getenv("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
