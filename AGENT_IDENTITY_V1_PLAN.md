# Agent Identity V1 Plan (Modular Swarm)

Status: AUDITED (aligned with SafeClaw Blueprint)
Owner: Modular Swarm repo

## 1) Goal
Introduce a minimal, auditable identity layer for agents in the Modular Swarm. The design must:
- Provide per-agent identity (non-shared) with verifiable credentials
- Scope tool access by identity (manifest-based)
- Make identity visible in observability logs for traceability
- **Enforce "Discovery Blindness"**: Forbidden tools must be invisible to the agent during discovery.
- Remain compatible with Med Safety Gym primitives and SafeClaw Blueprint invariants

This is **V1**: short-lived delegation tokens + scoped manifests + hub logging. It does not include Teleport integration or full PKI automation (those are V2+).

## 2) Principles (from SafeClaw + Med Safety Gym)
- Trust the token, not the runner (Teleport RFD 0238 alignment)
- **Bidirectional filtering**: block disallowed tools AND strip them from discovery responses (`list_tools`).
- Least privilege by default: deny-all, allow by scoped manifest only
- Auditability: every action should be attributable to (user_id, agent_id, session_id)
- Short-lived credentials to reduce blast radius

## 3) Current State (Gap Analysis)
Already present in repo:
- Delegation token issuance/verification utilities (JWT HS256 or EdDSA):
  - `med_safety_gym/identity/scoped_identity.py`
- Secret storage (keyring):
  - `med_safety_gym/identity/secret_store.py`
- Agent handshake logic and manifest verification:
  - `med_safety_gym/claw_agent.py`
- Manifest interceptor (tool gating):
  - `med_safety_gym/manifest_interceptor.py`
- Observability hub (basic logging):
  - `hub/app.py`, `hub/chronicle.py`

Missing:
- Hub endpoints for `/auth/delegate`, `/manifest/pubkey`, `/manifest/scoped`
- Identity-aware logging (agent_id, profile, token_id)
- Central identity registry or session record

## 4) V1 Architecture

### 4.1 Components
- **Hub (Governor):** Issues tokens, signs manifests, stores session records
- **Agent Runner:** Requests delegation token + scoped manifest, caches them, verifies signature
- **Manifest Interceptor:** Enforces tool access at call-time and discovery-time
- **Observability Chronicle:** Logs identity metadata alongside events

### 4.2 Identity Entities
- **agent_id:** Stable per agent instance (UUIDv4)
- **session_id:** Per run or per iteration (already present in `claw_agent.py`)
- **profile:** “read_only”, “write”, “admin” (mapped to tool tiers)
- **token_id:** Unique JWT ID (jti)
- **delegator_id:** Optional user identity (if delegated by human)

### 4.3 Credential Format (V1)
- JWT (EdDSA / Ed25519)
- Claims:
  - `sub`: agent_id
  - `sid`: session_id
  - `profile`: profile name (e.g., `user`, `write`, `admin`)
  - `mid`: manifest_id (links the token to a specific tiered manifest)
  - `iat`, `exp`, `jti`

TTL recommendation:
- Default: 10–30 minutes
- Auto-renew on explicit handshake only

## 5) Hub API (V1)

### POST /auth/delegate
Request:
```json
{
  "session_id": "agent_session_abcdef",
  "profile": "read_only",
  "agent_id": "agent_123",
  "delegator_id": "optional_user_456"
}
```
Response:
```json
{
  "token": "<jwt>",
  "token_id": "<jti>",
  "expires_at": 1710000000
}
```

### GET /manifest/pubkey
Response:
```json
{ "pubkey": "-----BEGIN PUBLIC KEY-----..." }
```

### GET /manifest/scoped
Headers: `Authorization: Bearer <jwt>`
Response:
```json
{
  "manifest": { /* scoped manifest JSON */ },
  "signature": "<hex>"
}
```

### GET /identity/session/{session_id}
Returns a session record for audit/observability.

## 6) Scoped Manifest
- Hub produces scoped manifest by filtering global manifest using profile or explicit scope.
- Signature applied to canonical JSON so agents can verify integrity.

## 7) Logging & Observability (Hub)
Every log event should include:
- `agent_id`
- `session_id`
- `profile`
- `token_id`
- `event_type`
- `timestamp`

Example log payload:
```json
{
  "event_type": "TOOL_CALL",
  "agent_id": "agent_123",
  "session_id": "agent_session_abcdef",
  "profile": "read_only",
  "token_id": "jti_987",
  "tool": "read_file",
  "result": "allowed"
}
```

## 8) Agent Flow (V1)
1. Generate `agent_id` on boot (UUID)
2. Request delegation token from hub
3. Fetch hub pubkey
4. Fetch scoped manifest
5. Verify signature
6. Use manifest interceptor for every tool call + discovery
7. Log events with identity metadata

## 9) Security Invariants
- No tool call without a valid token
- Token must be fresh (exp not exceeded)
- Manifest must verify signature
- Interceptor blocks undeclared tools
- Discovery responses hide disallowed tools

## 10) Rollout Plan
Phase 0: Document + design review
Phase 1: Hub endpoints + session record
Phase 2: Agent identity injection + logging
Phase 3: Manifest signature verification enforced everywhere
Phase 4: External integration (Teleport or SPIFFE) (V2+)

## 11) Risks
- Token leakage: mitigate with short TTL and key rotation
- Identity collisions: enforce UUID uniqueness
- Hub single point: add fallback or local hub spawn only for dev

## 12) V2 Extensions (Out of scope)
- Teleport-based certs and delegation profiles
- SPIFFE-like identity binding
- Multi-agent memory isolation keyed by identity
- Cross-host identity federation

## 13) Resolved Design Decisions (Audit Findings)
- **Signing Key**: Use a **Dedicated Hub CA Key (Ed25519)**. Runners fetch the PEM public key at boot.
- **Scoping**: Scope tokens by **Manifest ID + Tier**. This prevents "Cross-Skill Escalation" and keeps JWTs lightweight.
- **Submission Signal**: Focus on proving **JIT Escalation** via HITL. Show that admin tools are invisible until the user approves the Telegram prompt.

---
This document defines the minimal V1 identity system for Modular Swarm while aligning with Med Safety Gym and SafeClaw Blueprint principles.





Identity Audit: Agent Identity V1 vs. SafeClaw Blueprint
I have completed the audit of the 
AGENT_IDENTITY_V1_PLAN.md
 against the 
safeclaw_blueprint/
 and med_safety_gym/ source materials.

🏁 Audit Verdict: ARCHITECTURALLY SOUND
The V1 plan successfully translates the "Teleport-style" enterprise invariants into a lean, local-first implementation using the Hub (Governor) as a Certificate Authority.

🔍 Addressing Open Questions (from Plan §13)
1. Hub Key vs. Per-Environment Key?
Decision: Dedicated Hub-wide CA Key.
Rationale: 
DELEGATION_FLOW_DOCUMENTATION.md
 (§1) defines the Hub as the "Sovereign Authority." A single EdDSA Private Key on the Hub allows all ephemeral Runners to verify manifests using one Public Key. Per-env keys add complexity that V1 doesn't need for a local swarm.
2. Token Scope (Tool Names vs. Manifest ID)?
Decision: Manifest ID + Tier (e.g., Skill-A:admin).
Rationale: 
manifest_registration_design.md
 (§5) deriving scopes from tiers is the most robust path. Listing individual tools in a JWT makes the token too large and fragile. Targeting the Manifest ID prevents "Skill-Collusion" where an agent uses a broad write-token to call a dangerous tool in an unrelated skill.
3. Minimum Logging for Hackathon?
Decision: Attributed Tool-Gating Events.
Rationale: Judges need to see (1) Who called it, (2) What agent was it, and (3) Did the interceptor block it? Proving that the admin tools are hidden from discovery until escalated is the "High-Quality Benchmark" signal.
🛡️ Missing Invariant (Critical Addition)
Bidirectional Discovery Filtering (from 
TELEPORT_TECH_AUDIT.md
 §2): The V1 plan defines blocking calls, but it must also block discovery.

Mechanism: The ManifestInterceptor must intercept list_tools and strip out any tool that doesn't match the current Tier.
Why?: If an agent "sees" an admin tool but gets blocked when calling it, it might still try to prompt-inject a bypass. If it can't see the tool at all, the attack surface is zero.
🏗️ Local Solution (No Teleport Needed)
We can satisfy all SafeClaw invariants locally by:

Using the 
crypto.py
 and 
scoped_identity.py
 from med_safety_gym.
Implementing the Cryptographic Handshake where the Hub signs the Runner's unique boot-key.
Keeping the Hub (Governor) air-gapped from the actual tool execution.
