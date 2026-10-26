"""The Fuentio REST API (https://api.fuentio.com), with the user's own key.

One fixed host, HTTPS only; the country and identifier are placed in the path escaped, so an
input can never reach another host or path. The key travels in the `X-API-Key` header only and
never appears in an error message.
"""

import time
from typing import Any
from urllib.parse import quote

import requests

API = "https://api.fuentio.com"
TIMEOUT_S = 30
USER_AGENT = "fuentio-dify-plugin/0.0.1 (+https://fuentio.com)"
COUNTRIES = ("FR", "GB", "ES")
RETRYABLE = (429, 502, 503, 504)
MAX_WAIT_S = 5.0  # one retry when the API asks to wait this long or less


class FuentioError(Exception):
    """An answer the caller should see: the API's code, message and next step."""

    def __init__(self, code: str, message: str, hint: str | None = None) -> None:
        text = f"Fuentio {code}: {message}"
        super().__init__(f"{text} {hint}" if hint else text)
        self.code = code


def country_code(value: Any) -> str:
    code = str(value or "").strip().upper()
    if code not in COUNTRIES:
        raise FuentioError(
            "invalid_request",
            f"country must be FR, GB or ES (got {code or 'nothing'}).",
            "Fuentio covers France, the United Kingdom and Spain.",
        )
    return code


def identifier_part(value: Any) -> str:
    ident = str(value or "").strip()
    if not ident or len(ident) > 64:
        raise FuentioError(
            "invalid_request",
            "identifier must be an official ID of 1 to 64 characters, never a company name.",
            "With a name, call search_companies first and use an ID from its results.",
        )
    return quote(ident, safe="")


def company_path(country: Any, identifier: Any, tail: str = "") -> str:
    return f"/v1/companies/{country_code(country)}/{identifier_part(identifier)}{tail}"


def clean(params: dict[str, Any]) -> dict[str, Any]:
    """Only the parameters the user gave."""
    return {k: v for k, v in params.items() if v not in (None, "")}


def call(
    api_key: str,
    method: str,
    path: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> dict[str, Any]:
    headers = {
        "X-API-Key": api_key,
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    }
    for attempt in range(2):
        try:
            response = requests.request(
                method,
                API + path,
                params=params,
                json=body,
                headers=headers,
                timeout=TIMEOUT_S,
            )
        except requests.RequestException as exc:
            raise FuentioError(
                "upstream_unavailable",
                f"Fuentio could not be reached ({type(exc).__name__}).",
                "Retry in a minute.",
            ) from None
        if response.status_code in RETRYABLE and attempt == 0:
            wait = _retry_after(response)
            if wait is not None and wait <= MAX_WAIT_S:
                time.sleep(wait)
                continue
        try:
            payload = response.json()
        except ValueError:
            payload = {}
        if response.status_code >= 400 or not isinstance(payload, dict):
            error = (payload.get("error") if isinstance(payload, dict) else None) or {}
            raise FuentioError(
                str(error.get("code") or f"http_{response.status_code}"),
                str(error.get("message") or "The request failed."),
                error.get("hint"),
            )
        return payload
    raise FuentioError("rate_limited", "Too many requests.", "Retry in a few seconds.")


def _retry_after(response: requests.Response) -> float | None:
    try:
        return max(0.0, float(response.headers.get("Retry-After", "")))
    except ValueError:
        return None


# ---- one line an agent or a person can read ---------------------------------------------------


def primary_id(company: dict[str, Any]) -> str:
    for ident in company.get("identifiers") or []:
        if ident.get("primary"):
            return str(ident.get("value") or "")
    return str(company.get("id") or "")


def name_of(company: dict[str, Any]) -> str:
    name = company.get("name") or {}
    return str(name.get("original") if isinstance(name, dict) else name or "")


def status_of(company: dict[str, Any]) -> str:
    status = company.get("status") or {}
    return str(status.get("value") if isinstance(status, dict) else status or "unknown")
