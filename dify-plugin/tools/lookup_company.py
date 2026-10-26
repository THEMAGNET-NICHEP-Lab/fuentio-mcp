from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.fuentio_client import call, clean, company_path, name_of, primary_id, status_of


class LookupCompanyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        path = company_path(tool_parameters.get("country"), tool_parameters.get("identifier"))
        answer = call(
            self.runtime.credentials["fuentio_api_key"],
            "GET",
            path,
            params=clean({"id_scheme": tool_parameters.get("id_scheme")}),
        )
        company = answer.get("data") or {}
        meta = answer.get("meta") or {}
        provenance = company.get("provenance") or {}
        checked = str(meta.get("last_verified_at") or provenance.get("last_verified_at") or "")
        source = str(meta.get("source") or provenance.get("source") or "")
        yield self.create_text_message(
            f"{name_of(company)} ({company.get('country')} {primary_id(company)}): "
            f"{status_of(company)}. Source: {source}, checked {checked[:10]}"
            + (f" ({provenance['source_url']})." if provenance.get("source_url") else ".")
        )
        yield self.create_json_message(answer)
        yield self.create_variable_message("company_name", name_of(company))
        yield self.create_variable_message("official_id", primary_id(company))
        yield self.create_variable_message("status", status_of(company))
        yield self.create_variable_message("source", source)
        yield self.create_variable_message("checked_at", checked)
