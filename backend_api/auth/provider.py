"""
Auth Provider — OAuth2/OpenID Connect authentication via Keycloak.
Validates JWT tokens and provides user identity for API endpoints.
"""

import logging
import os
from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)

KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "aspar")
KEYCLOAK_CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "aspar-hub")

_bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class User:
    """Authenticated user identity."""
    sub: str
    email: str | None
    name: str | None
    roles: list[str]
    raw_token: dict[str, Any]

    def has_role(self, role: str) -> bool:
        """Check if the user has a specific role."""
        return role in self.roles


async def verify_token(token: str) -> dict[str, Any]:
    """Verify a JWT token against the Keycloak userinfo endpoint."""
    userinfo_url = (
        f"{KEYCLOAK_BASE_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
    )
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            userinfo_url,
            headers={"Authorization": f"Bearer {token}"},
        )
    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return response.json()


def _extract_roles(token_payload: dict[str, Any]) -> list[str]:
    """Extract realm and client roles from a Keycloak token payload."""
    roles: list[str] = []
    realm_access = token_payload.get("realm_access", {})
    roles.extend(realm_access.get("roles", []))
    resource_access = token_payload.get("resource_access", {})
    client_roles = resource_access.get(KEYCLOAK_CLIENT_ID, {})
    roles.extend(client_roles.get("roles", []))
    return roles


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> User:
    """
    FastAPI dependency that validates the Bearer token and returns the current user.

    In development mode (no KEYCLOAK_URL set), returns a mock admin user.
    """
    if not os.getenv("KEYCLOAK_URL"):
        # Development mode: bypass auth
        logger.warning("Auth bypass active — set KEYCLOAK_URL to enable authentication")
        return User(
            sub="dev-user",
            email="dev@aspar.team",
            name="Dev User",
            roles=["admin", "engineer"],
            raw_token={},
        )

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = await verify_token(credentials.credentials)
    return User(
        sub=payload.get("sub", ""),
        email=payload.get("email"),
        name=payload.get("name"),
        roles=_extract_roles(payload),
        raw_token=payload,
    )


def require_role(role: str):
    """FastAPI dependency factory to require a specific role."""
    async def _dependency(user: User = Depends(get_current_user)) -> User:
        if not user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' required",
            )
        return user
    return _dependency
