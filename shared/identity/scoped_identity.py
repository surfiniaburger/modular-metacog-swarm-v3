from typing import List, Dict, Any
import jwt
import time
import uuid
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key

def create_scoped_manifest(global_manifest: Dict[str, List[Any]], allowed_tools: List[str]) -> Dict[str, List[Any]]:
    """
    Filters a tiered manifest dictionary to only include tools present in the allowed_tools list.
    Preserves the tier keys (user, write, admin, critical).
    """
    scoped = {}
    for tier, tools in global_manifest.items():
        if isinstance(tools, list):
            scoped[tier] = [t for t in tools if (t.get("name") if isinstance(t, dict) else t) in allowed_tools]
        else:
            scoped[tier] = tools
    return scoped

def issue_delegation_token(claims: Dict[str, Any], ttl_seconds: int, signing_key: str) -> str:
    """
    Issues a signed delegation token (JWT) with jti per V1 Plan §4.3.
    Supports both HS256 (symmetric) and EdDSA (asymmetric Ed25519).
    """
    payload = claims.copy()
    payload["iat"] = int(time.time())
    payload["exp"] = payload["iat"] + ttl_seconds
    payload["jti"] = str(uuid.uuid4())  # Unique token ID for auditability
    
    if "-----BEGIN" in signing_key:
        key = load_pem_private_key(signing_key.encode(), password=None)
        return jwt.encode(payload, key, algorithm="EdDSA")
    else:
        return jwt.encode(payload, signing_key, algorithm="HS256")


def verify_delegation_token(token: str, verification_key: str) -> Dict[str, Any]:
    """
    Verifies a delegation token and returns its decoded claims.
    """
    is_pem = "-----BEGIN" in verification_key if isinstance(verification_key, str) else b"-----BEGIN" in verification_key
    
    if is_pem:
        key_bytes = verification_key.encode() if isinstance(verification_key, str) else verification_key
        key = load_pem_public_key(key_bytes)
        return jwt.decode(token, key, algorithms=["EdDSA"])
    else:
        return jwt.decode(token, verification_key, algorithms=["HS256"])

