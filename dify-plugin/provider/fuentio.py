from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from tools.fuentio_client import FuentioError, call


class FuentioProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        """The key is checked with `GET /v1/usage`: free, and refused for an unknown or revoked
        key. Nothing else is sent."""
        key = str(credentials.get("fuentio_api_key") or "").strip()
        if not key:
            raise ToolProviderCredentialValidationError("Enter your Fuentio API key.")
        try:
            call(key, "GET", "/v1/usage")
        except FuentioError as exc:
            raise ToolProviderCredentialValidationError(str(exc)) from None
