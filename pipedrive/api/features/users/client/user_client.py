from typing import Any, Dict, List

from log_config import logger
from pipedrive.api.base_client import BaseClient


class UserClient:
    """Client for Pipedrive User API endpoints (v1, read-only)."""

    def __init__(self, base_client: BaseClient):
        self.base_client = base_client

    async def list_users(self) -> List[Dict[str, Any]]:
        """List all users in the Pipedrive account.

        Pipedrive's /users endpoint returns the full set without pagination.
        """
        logger.info("UserClient: listing users")
        response = await self.base_client.request("GET", "/users", version="v1")
        return response.get("data", []) or []

    async def get_user(self, user_id: int) -> Dict[str, Any]:
        """Get a single user by ID."""
        logger.info(f"UserClient: getting user {user_id}")
        if user_id <= 0:
            raise ValueError(
                f"Invalid user_id: {user_id}. Must be a positive integer."
            )
        response = await self.base_client.request(
            "GET", f"/users/{user_id}", version="v1"
        )
        return response.get("data", {}) or {}
