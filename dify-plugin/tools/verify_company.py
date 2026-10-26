from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.fuentio_client import FuentioError, call, clean, country_code, identifier_part, name_of


class VerifyCompanyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        country = country_code(tool_parameters.get("country"))
        identifier_part(tool_parameters.get("identifier"))  # same rule as the other tools
        reference = str(tool_parameters.get("reference") or "").strip()
        if len(reference) > 200:
            raise FuentioError("invalid_request", "reference is at most 200 characters.")
        answer = call(
            self.runtime.credentials["fuentio_api_key"],
            "POST",
            "/v1/verifications",
            body=clean(
                {
                    "country": country,
                    "identifier": str(tool_parameters.get("identifier")).strip(),
                    "id_scheme": tool_parameters.get("id_scheme"),
                    "reference": reference,
                }
            ),
        )
        data = answer.get("data") or {}
        result = data.get("result") or {}
        company = data.get("company") or {}
        outcome = str(result.get("outcome") or "")
        reasons = [str(r) for r in result.get("reasons") or []]
        proof = str(data.get("proof_code") or "")
        checked = str(data.get("checked_at") or "")
        ident = data.get("identifier")  # {"scheme": "FR_SIREN", "value": "552032534"}
        shown = ident.get("value") if isinstance(ident, dict) else ident
        shown = str(shown or tool_parameters.get("identifier") or "").strip()
        yield self.create_text_message(
            f"{name_of(company) or shown} ({country} {shown}): "
            f"{outcome}"
            + (f" ({', '.join(reasons)})" if reasons else "")
            + f". Proof code {proof}, checked {checked[:10]}. "
            "A registry check, not full KYB, UBO proof or sanctions clearance."
        )
        yield self.create_json_message(answer)
        yield self.create_variable_message("outcome", outcome)
        yield self.create_variable_message("reasons", ", ".join(reasons))
        yield self.create_variable_message("proof_code", proof)
        yield self.create_variable_message("company_name", name_of(company))
        yield self.create_variable_message("checked_at", checked)
