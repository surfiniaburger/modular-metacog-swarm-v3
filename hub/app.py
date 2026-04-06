# hub/app.py
from fastapi import FastAPI, Request, HTTPException
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any

# Modular Identity Imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.identity.crypto import generate_keys, export_private_key, export_public_key, load_private_key, load_public_key
from shared.identity.scoped_identity import issue_delegation_token
from shared.identity.secret_store import get_default_store

app = FastAPI(title="Sovereign Swarm Governor")
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("hub")

CHRONICLE_PATH = "research_env/docs/research_chronicle.md"
os.makedirs("research_env/docs", exist_ok=True)

secret_store = get_default_store()

# State for Authority
CA_PRIVATE_KEY_BYTES = None
CA_PUBLIC_KEY_PEM = None

@app.on_event("startup")
async def startup():
    global CA_PRIVATE_KEY_BYTES, CA_PUBLIC_KEY_PEM
    
    # Try fetching keys from the OS keyring / secret store
    stored_priv = secret_store.get_secret("ca_private_key")
    stored_pub = secret_store.get_secret("ca_public_key")
    
    if stored_priv and stored_pub:
        logger.info("Loaded Sovereign CA Key Pair from Secret Store (Keyring).")
        CA_PRIVATE_KEY_BYTES = stored_priv.encode()
        CA_PUBLIC_KEY_PEM = stored_pub
    else:
        logger.info("Generating new Sovereign CA Key Pair and persisting to Secret Store...")
        priv_obj, pub_obj = generate_keys()
        
        # Serialize to PEM
        priv_pem = export_private_key(priv_obj)
        pub_pem = export_public_key(pub_obj)
        
        CA_PRIVATE_KEY_BYTES = priv_pem
        CA_PUBLIC_KEY_PEM = pub_pem.decode()
        
        # Save securely to Keyring
        secret_store.set_secret("ca_private_key", CA_PRIVATE_KEY_BYTES.decode())
        secret_store.set_secret("ca_public_key", CA_PUBLIC_KEY_PEM)

    if not os.path.exists(CHRONICLE_PATH):
        with open(CHRONICLE_PATH, "w") as f:
            f.write("# Research Chronicle\n\n## Era 1: Initialization\nSovereign Governor spawned.")

@app.get("/auth/pubkey")
async def get_pubkey():
    return {"pubkey": CA_PUBLIC_KEY_PEM}

@app.post("/auth/delegate")
async def delegate_identity(request: Request):
    """
    Issues a signed delegation token for an agent per V1 Plan §5.
    Including mid (Manifest ID) per SafeClaw.
    """
    data = await request.json()
    agent_id = data.get("agent_id")
    profile = data.get("profile", "read_only")
    session_id = data.get("session_id", "")
    
    if not agent_id:
        raise HTTPException(status_code=400, detail="agent_id required")
        
    mid = f"manifest-{profile}-v1"
        
    claims = {
        "sub": agent_id,
        "profile": profile,
        "sid": session_id,
        "mid": mid,
        "iss": "Governor"
    }
    
    token = issue_delegation_token(claims, ttl_seconds=3600, signing_key=CA_PRIVATE_KEY_BYTES.decode())
    
    # Decode to extract jti for the response
    import jwt as _jwt
    decoded = _jwt.decode(token, options={"verify_signature": False})
    
    return {"token": token, "agent_id": agent_id, "token_id": decoded.get("jti", ""), "manifest_id": mid}

@app.get("/manifest/scoped")
async def get_scoped_manifest(request: Request):
    """
    Returns the Hub-signed scoped manifest matching the provided token's `mid`.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = auth_header.split(" ")[1]
    
    import jwt as _jwt
    try:
        # We verify signature and exp right here on the hub before issuing manifest
        claims = _jwt.decode(token, CA_PUBLIC_KEY_PEM, algorithms=["EdDSA"])
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
        
    profile = claims.get("profile", "read_only")
    mid = claims.get("mid", "manifest-unknown-v1")
    
    # 1. Construct the tier-based tools array
    tools = ["read_file", "list_dir", "run_benchmark"]
    if profile == "executor":
        tools += ["write_to_file", "replace_file_content"]
    elif profile == "admin":
        tools += ["run_command", "git_push"]
        
    manifest_data = {
        "name": f"agent-{claims.get('sub')}",
        "manifest_id": mid,
        "permissions": {
            "tools": {"user": tools}
        }
    }
    
    # 2. Convert to canonical JSON and cryptographically sign the raw bytes
    from shared.identity.crypto import sign_data, load_private_key
    import json
    
    canonical_manifest_bytes = json.dumps(manifest_data, separators=(',', ':'), sort_keys=True).encode('utf-8')
    private_key_obj = load_private_key(CA_PRIVATE_KEY_BYTES)
    raw_signature = sign_data(canonical_manifest_bytes, private_key_obj)
    
    return {
        "manifest": manifest_data,
        "signature": raw_signature.hex()
    }

@app.post("/log")
async def log_event(request: Request):
    """
    Identity-aware structured logging per V1 Plan §7.
    """
    data = await request.json()
    event_type = data.get("event_type", "GENERIC")
    agent_id = data.get("agent_id", "ANONYMOUS")
    profile = data.get("profile", "UNKNOWN")
    session_id = data.get("session_id", "")
    token_id = data.get("token_id", "NO_TOKEN")
    manifest_id = data.get("manifest_id", "NO_MANIFEST")
    content = data.get("data", "")
    timestamp = datetime.utcnow().isoformat()
    
    # Sovereign chronicle entry with full attribution
    sid_tag = f" | Session: {session_id}" if session_id else ""
    token_tag = f" | TokenID: {token_id} | ManifestID: {manifest_id}"
    entry = f"\n\n### [{timestamp}] {event_type} | Agent: {agent_id} ({profile}){sid_tag}{token_tag}\n{content}"
    
    with open(CHRONICLE_PATH, "a") as f:
        f.write(entry)
        
    logger.info(f"Logged {event_type} from {agent_id} ({profile}|{manifest_id}) to Chronicle.")
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
