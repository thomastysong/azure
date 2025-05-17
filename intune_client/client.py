"""Client for managing Intune profiles via Microsoft Graph."""
from typing import Dict, Any, Protocol, runtime_checkable

import json
import urllib.request
import urllib.error


@runtime_checkable
class TokenCredentialProtocol(Protocol):
    """Minimal protocol for Azure credentials."""

    def get_token(self, *scopes: str):
        """Return an access token for the given scopes."""
        ...


class IntuneClient:
    """Microsoft Intune management client using Microsoft Graph."""

    def __init__(self, credential: TokenCredentialProtocol, *, endpoint: str = "https://graph.microsoft.com/beta") -> None:
        """Initialize the client.

        Parameters
        ----------
        credential:
            Object implementing ``get_token`` returning an access token for
            Microsoft Graph.
        endpoint:
            Base URL for Microsoft Graph. Defaults to the beta endpoint.
        """
        self._credential = credential
        self._endpoint = endpoint.rstrip("/")

    def _get_token(self) -> str:
        token = self._credential.get_token("https://graph.microsoft.com/.default")
        return token.token

    def _headers(self) -> Dict[str, str]:
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, url: str, data: Dict[str, Any] | None = None) -> Dict[str, Any]:
        body = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, method=method, headers=self._headers())
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read()
                if content:
                    return json.loads(content)
                return {}
        except urllib.error.HTTPError as exc:
            msg = exc.read().decode()
            raise RuntimeError(f"Request failed: {exc.code} {msg}") from exc

    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a device configuration profile."""
        url = f"{self._endpoint}/deviceManagement/deviceConfigurations"
        return self._request("POST", url, profile_data)

    def update_profile(self, profile_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing device configuration profile."""
        url = f"{self._endpoint}/deviceManagement/deviceConfigurations/{profile_id}"
        return self._request("PATCH", url, profile_data)

    def delete_profile(self, profile_id: str) -> None:
        """Delete a device configuration profile."""
        url = f"{self._endpoint}/deviceManagement/deviceConfigurations/{profile_id}"
        self._request("DELETE", url)

    def modify_assignments(self, profile_id: str, assignments: Dict[str, Any]) -> Dict[str, Any]:
        """Modify assignments for the specified profile."""
        url = f"{self._endpoint}/deviceManagement/deviceConfigurations/{profile_id}/assign"
        return self._request("POST", url, assignments)
