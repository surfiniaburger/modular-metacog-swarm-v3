import uuid
import requests
import logging
import time
from typing import Dict, List, Any, Optional

from shared.identity.scoped_identity import verify_delegation_token
from shared.identity.manifest_interceptor import ManifestInterceptor
from shared.identity.skill_manifest import SkillManifest

logger = logging.getLogger("identity_guard")

class SovereignIdentityGuard:
    """
    Handles the cryptographic handshake with the Hub and enforces Discovery Blindness.
    """
    def __init__(self, hub_url: str = "http://localhost:8000", session_id: str = ""):
        self.hub_url = hub_url
        self.session_id = session_id
        self.agent_id = str(uuid.uuid4())
        self.token = None
        self.token_id = None
        self.manifest_id = None
        self.pubkey = None
        self.manifest = None
        self.interceptor = None

    def handshake(self, profile: str = "read_only", retries: int = 5, delay: int = 2):
        """
        Performs the Sovereign Handshake with the Hub with retry resilience.
        """
        for i in range(retries):
            try:
                # 1. Fetch Hub Pubkey
                resp = requests.get(f"{self.hub_url}/auth/pubkey", timeout=5)
                if resp.status_code != 200:
                    raise RuntimeError(f"Hub returned {resp.status_code}")
                self.pubkey = resp.json()["pubkey"]
                
                # 2. Request Delegation Token
                resp = requests.post(
                    f"{self.hub_url}/auth/delegate",
                    json={"agent_id": self.agent_id, "profile": profile, "session_id": self.session_id},
                    timeout=5
                )
                if resp.status_code != 200:
                    raise RuntimeError(f"Delegation failed: {resp.text}")
                data = resp.json()
                self.token = data["token"]
                self.token_id = data.get("token_id")
                self.manifest_id = data.get("manifest_id")
                
                # 3. Verify Token locally (checks exp)
                claims = verify_delegation_token(self.token, self.pubkey)
                
                # 4. Fetch Hub-signed scoped manifest
                manifest_resp = requests.get(
                    f"{self.hub_url}/manifest/scoped",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=5
                )
                if manifest_resp.status_code != 200:
                    raise RuntimeError(f"Manifest fetch failed: {manifest_resp.text}")
                
                m_data = manifest_resp.json()
                manifest_payload = m_data["manifest"]
                manifest_sig = m_data["signature"]
                
                # 5. Verify manifest signature using raw canonical JSON
                from shared.identity.crypto import verify_signature, load_public_key
                import json
                
                canonical_manifest_bytes = json.dumps(manifest_payload, separators=(',', ':'), sort_keys=True).encode('utf-8')
                sig_bytes = bytes.fromhex(manifest_sig)
                pubkey_obj = load_public_key(self.pubkey.encode())
                
                if not verify_signature(canonical_manifest_bytes, sig_bytes, pubkey_obj):
                    raise RuntimeError("Sovereign Violation: Manifest signature is invalid or tampered.")
                
                if manifest_payload.get("manifest_id") != self.manifest_id:
                    raise RuntimeError("Sovereign Violation: Manifest ID mismatch against expected mid.")
                if claims.get("profile") != profile:
                    raise RuntimeError("Sovereign Violation: Token profile mismatch.")
                
                logger.info(f"Handshake successful. Agent: {self.agent_id} | Profile: {profile} | Manifest: {self.manifest_id}")
                
                self.manifest = SkillManifest.from_dict(manifest_payload)
                self.interceptor = ManifestInterceptor(self.manifest)
                return # SUCCESS
                
            except Exception as e:
                if i == retries - 1:
                    logger.error(f"Sovereign Handshake failed after {retries} attempts: {e}")
                    raise RuntimeError("Identity bootstrap failure. Critical Safety Violation.")
                
                logger.warning(f"Hub not ready ({e}). Retrying in {delay}s... ({i+1}/{retries})")
                time.sleep(delay)
                delay *= 2

    def check_freshness(self) -> bool:
        """
        Enforce token freshness per Phase 5.
        Decodes the local token to check if 'exp' is approaching.
        Returns True if fresh, False if expired/expiring.
        """
        if not self.token: return False
        try:
            import jwt as _jwt
            claims = _jwt.decode(self.token, options={"verify_signature": False})
            exp = claims.get("exp", 0)
            if exp - time.time() < 300: # Refresh if < 5 mins remain
                return False
            return True
        except Exception:
            return False

    def enforce_freshness(self, profile: str = "read_only"):
        """Checks validation and re-handshakes if necessary."""
        if not self.check_freshness():
            logger.info(f"Token expired/expiring for profile {profile}. Renewing handshake...")
            self.handshake(profile=profile)

    def _initialize_manifest(self, profile: str):
        """
        Surgically defines permissions based on the identity profile.
        """
        # Baseline research tools
        tools = ["read_file", "list_dir", "run_benchmark"]
        
        if profile == "executor":
            tools += ["write_to_file", "replace_file_content"]
        elif profile == "admin":
            tools += ["run_command", "git_push"]
            
        manifest_data = {
            "name": f"agent-{self.agent_id}",
            "permissions": {
                "tools": {"user": tools}
            }
        }
        self.manifest = SkillManifest.from_dict(manifest_data)
        self.interceptor = ManifestInterceptor(self.manifest)

    def filter_discovery(self, available_tools: List[str]) -> List[str]:
        """
        ENFORCES DISCOVERY BLINDNESS.
        Strips disallowed tools from the agent's view.
        """
        if not self.manifest:
            return []
        
        allowed = self.manifest.permissions.tools.all_tools
        filtered = [t for t in available_tools if t in allowed]
        
        blind_count = len(available_tools) - len(filtered)
        if blind_count > 0:
            logger.warning(f"Discovery Blindness active: Stripped {blind_count} unauthorized tools.")
            
        return filtered

    def audit_log(self, event_type: str, data: str, profile: str):
        """
        Sends identity-attributed logs to the Hub, including strict V1 token and manifest metadata.
        """
        try:
            requests.post(
                f"{self.hub_url}/log",
                json={
                    "event_type": event_type,
                    "agent_id": self.agent_id,
                    "profile": profile,
                    "session_id": self.session_id,
                    "token_id": self.token_id,
                    "manifest_id": self.manifest_id,
                    "data": data
                },
                timeout=5
            )
        except Exception:
            pass # Non-blocking log failure
