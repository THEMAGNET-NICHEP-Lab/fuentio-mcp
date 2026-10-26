"""The Fuentio Dify plugin: loads as the runtime loads it, and each tool calls the right Fuentio
endpoint with the user's own key (API mocked)."""

import json
from pathlib import Path
from typing import Any

import pytest
import responses
from dify_plugin.config.config import DifyPluginEnv
from dify_plugin.core.plugin_registration import PluginRegistration
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

API = "https://api.fuentio.com"
KEY = "sk_live_" + "t" * 32
TOOLS = (
    "search_companies",
    "lookup_company",
    "verify_company",
    "check_insolvency",
    "get_company_history",
)
CH = "https://find-and-update.company-information.service.gov.uk/company/"


def company(name: str = "TESCO PLC", number: str = "00445790") -> dict[str, Any]:
    return {
        "id": f"GB-COMPANYNUMBER-{number}",
        "country": "GB",
        "identifiers": [{"scheme": "GB_COMPANY_NUMBER", "value": number, "primary": True}],
        "name": {"original": name},
        "status": {"value": "active", "original_label": "Active"},
        "provenance": {
            "source": "gb_companies_house_api",
            "source_url": CH + number,
            "last_verified_at": "2026-10-26T09:00:00+00:00",
        },
    }


def envelope(data: Any, **meta: Any) -> dict[str, Any]:
    return {"data": data, "meta": meta, "error": None}


def error(code: str, message: str, hint: str) -> dict[str, Any]:
    return {"data": None, "error": {"code": code, "message": message, "hint": hint}}


def run(tool_name: str, params: dict[str, Any]) -> list[ToolInvokeMessage]:
    registration = PluginRegistration(DifyPluginEnv())
    tool_cls = registration.get_tool_cls("fuentio", tool_name)
    assert tool_cls is not None
    return list(tool_cls.from_credentials({"fuentio_api_key": KEY}).invoke(params))


def texts(messages: list[ToolInvokeMessage]) -> list[str]:
    return [m.message.text for m in messages if m.type == ToolInvokeMessage.MessageType.TEXT]


def jsons(messages: list[ToolInvokeMessage]) -> list[dict[str, Any]]:
    kind = ToolInvokeMessage.MessageType.JSON
    return [m.message.json_object for m in messages if m.type == kind]


def variables(messages: list[ToolInvokeMessage]) -> dict[str, Any]:
    return {
        m.message.variable_name: m.message.variable_value
        for m in messages
        if m.type == ToolInvokeMessage.MessageType.VARIABLE
    }


# ---- the package as Dify loads it ------------------------------------------------------------


def test_the_runtime_loads_the_manifest_the_provider_and_every_tool() -> None:
    registration = PluginRegistration(DifyPluginEnv())
    manifest = registration.configuration
    assert (manifest.author, manifest.name, manifest.version) == ("fuentio", "fuentio", "0.0.1")
    [provider] = registration.tools_configuration
    assert provider.identity.name == "fuentio"
    assert [c.name for c in provider.credentials_schema] == ["fuentio_api_key"]
    assert provider.credentials_schema[0].type.value == "secret-input"
    assert registration.get_tool_provider_cls("fuentio") is not None
    for name in TOOLS:
        assert registration.get_tool_cls("fuentio", name) is not None, name


def test_no_text_claims_more_than_a_registry_check() -> None:
    shipped = "\n".join(
        p.read_text(encoding="utf-8")
        for p in Path(".").rglob("*")
        if p.is_file() and p.suffix in (".yaml", ".md", ".py") and "tests" not in p.parts
    ).lower()
    for claim in ("full kyb check", "aml check", "ubo data", "guarantee"):
        assert claim not in shipped, claim
    assert "not full kyb" in shipped and "no person's name" in shipped


# ---- the credential ------------------------------------------------------------------------------


@responses.activate
def test_the_key_is_checked_with_a_free_call_and_a_bad_key_is_refused() -> None:
    provider = PluginRegistration(DifyPluginEnv()).get_tool_provider_cls("fuentio")()
    responses.get(f"{API}/v1/usage", json=envelope({"plan": "free"}))
    provider._validate_credentials({"fuentio_api_key": KEY})
    assert responses.calls[0].request.headers["X-API-Key"] == KEY
    assert "fuentio-dify-plugin" in responses.calls[0].request.headers["User-Agent"]

    responses.get(
        f"{API}/v1/usage",
        status=401,
        json=error("unauthorized", "This API key is unknown or revoked.", "Get a free key."),
    )
    with pytest.raises(ToolProviderCredentialValidationError) as refused:
        provider._validate_credentials({"fuentio_api_key": KEY})
    assert "unauthorized" in str(refused.value) and KEY not in str(refused.value)
    with pytest.raises(ToolProviderCredentialValidationError, match="Enter your"):
        provider._validate_credentials({"fuentio_api_key": "  "})


# ---- the tools -----------------------------------------------------------------------------------


@responses.activate
def test_search_sends_the_name_and_filters_and_lists_the_matches() -> None:
    row = {**company(), "match": {"score": 0.95, "band": "strong"}}
    responses.get(
        f"{API}/v1/companies/search", json=envelope([row], page=1, total=1, next_page=None)
    )
    out = run("search_companies", {"country": "gb", "query": " tesco ", "page": 1})
    assert responses.calls[0].request.params == {"country": "GB", "q": "tesco", "page": "1"}
    assert "1. TESCO PLC — GB 00445790 — active (match 0.95, strong)" in texts(out)[0]
    assert jsons(out)[0]["data"][0]["id"] == "GB-COMPANYNUMBER-00445790"


@responses.activate
def test_lookup_reads_one_company_and_gives_its_source_and_check_date() -> None:
    responses.get(
        f"{API}/v1/companies/GB/00445790",
        json=envelope(
            company(),
            source="gb_companies_house_api",
            last_verified_at="2026-10-26T09:00:00+00:00",
        ),
    )
    out = run("lookup_company", {"country": "GB", "identifier": "00445790"})
    assert texts(out)[0].startswith("TESCO PLC (GB 00445790): active. Source: gb_companies")
    assert variables(out) == {
        "company_name": "TESCO PLC",
        "official_id": "00445790",
        "status": "active",
        "source": "gb_companies_house_api",
        "checked_at": "2026-10-26T09:00:00+00:00",
    }


@responses.activate
def test_an_identifier_never_leaves_its_path_segment_or_reaches_another_host() -> None:
    from tools.fuentio_client import FuentioError

    responses.get(f"{API}/v1/companies/FR/..%2Fusage%3Fx%3D1", json=envelope(company()))
    run("lookup_company", {"country": "FR", "identifier": "../usage?x=1"})
    assert responses.calls[0].request.url == f"{API}/v1/companies/FR/..%2Fusage%3Fx%3D1"
    with pytest.raises(FuentioError, match="country must be FR, GB or ES"):
        run("lookup_company", {"country": "DE", "identifier": "HRB 1"})
    with pytest.raises(FuentioError, match="never a company name"):
        run("lookup_company", {"country": "FR", "identifier": "x" * 65})
    assert len(responses.calls) == 1  # refused before any call


@responses.activate
def test_verify_posts_the_check_and_gives_the_outcome_to_branch_on() -> None:
    responses.post(
        f"{API}/v1/verifications",
        json=envelope(
            {
                "identifier": {"scheme": "FR_SIREN", "value": "345086177"},  # as production
                "proof_code": "FUE-FR-20261026-5ZNCGZ",
                "checked_at": "2026-10-26T10:00:00+00:00",
                "company": {"name": {"original": "CAMAIEU INTERNATIONAL"}},
                "result": {"outcome": "unverified", "reasons": ["insolvency_liquidation"]},
            }
        ),
    )
    params = {"country": "FR", "identifier": " 345086177 ", "reference": "SUP-1"}
    out = run("verify_company", params)
    assert json.loads(responses.calls[0].request.body) == {
        "country": "FR",
        "identifier": "345086177",
        "reference": "SUP-1",
    }
    assert variables(out)["outcome"] == "unverified"
    assert variables(out)["proof_code"] == "FUE-FR-20261026-5ZNCGZ"
    assert texts(out)[0].startswith(
        "CAMAIEU INTERNATIONAL (FR 345086177): unverified (insolvency_liquidation). "
        "Proof code FUE-FR-20261026-5ZNCGZ, checked 2026-10-26."
    )
    assert "not full KYB" in texts(out)[0]


@responses.activate
def test_insolvency_and_history_answer_with_their_state() -> None:
    responses.get(
        f"{API}/v1/companies/FR/345086177/insolvency",
        json=envelope(
            {
                "state": "in_procedure",
                "procedure": "liquidation",
                "opened_on": "2020-09-28",
                "notices": [{}, {}],
                "covered_since": "2008-01-01",
            }
        ),
    )
    out = run("check_insolvency", {"country": "FR", "identifier": "345086177"})
    assert texts(out)[0].startswith("Insolvency state for FR 345086177: in_procedure (liquidation")
    assert variables(out)["state"] == "in_procedure"

    responses.get(
        f"{API}/v1/companies/ES/VI-23266/history",
        json=envelope(
            {"name": "X SL", "snapshots": [{}], "events": [{}, {}]}, history_since="2009-01-02"
        ),
    )
    out = run("get_company_history", {"country": "ES", "identifier": "VI-23266"})
    assert texts(out)[0] == (
        "X SL: 1 version(s) and 2 dated event(s) on this page; history since 2009-01-02."
    )


@responses.activate
def test_an_api_error_is_shown_with_its_next_step_never_with_the_key() -> None:
    from tools.fuentio_client import FuentioError

    responses.get(
        f"{API}/v1/companies/FR/123456789",
        status=404,
        json=error(
            "not_found",
            "No company found for SIREN 123456789.",
            "Check the number, or search by name.",
        ),
    )
    with pytest.raises(FuentioError) as failed:
        run("lookup_company", {"country": "FR", "identifier": "123456789"})
    assert str(failed.value) == (
        "Fuentio not_found: No company found for SIREN 123456789. Check the number, or search by "
        "name."
    )
    assert KEY not in str(failed.value)
