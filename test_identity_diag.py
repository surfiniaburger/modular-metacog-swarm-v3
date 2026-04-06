import sys
import os

# Align path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

try:
    from shared.identity.crypto import generate_keys, export_private_key
    from shared.identity.scoped_identity import issue_delegation_token
    
    print("Generating keys...")
    priv_obj, pub_obj = generate_keys()
    priv_pem = export_private_key(priv_obj).decode()
    
    print("Issuing token...")
    claims = {"sub": "test-agent", "profile": "admin"}
    token = issue_delegation_token(claims, ttl_seconds=3600, signing_key=priv_pem)
    
    print(f"Token issued successfully: {token[:20]}...")
    print("DIAGNOSTIC_SUCCESS")

except Exception as e:
    print(f"DIAGNOSTIC_FAILURE: {e}")
    import traceback
    traceback.print_exc()
