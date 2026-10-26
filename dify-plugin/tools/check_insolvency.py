from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.fuentio_client import call, company_path


class CheckInsolvencyTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        country = str(tool_parameters.get("country") or "").upper()
        identifier = str(tool_parameters.get("identifier") or "").strip()
        answer = call(
            self.runtime.credentials["fuentio_api_key"],
            "GET",
            company_path(country, identifier, "/insolvency"),
        )
        data = answer.get("data") or {}
        state = str(data.get("state") or "")
        procedure = data.get("procedure")
        notices = data.get("notices") or []
        since = str(data.get("covered_since") or "")
        text = f"Insolvency state for {country} {identifier}: {state}"
        if procedure:
            text += f" ({procedure}"
            text += f", opened {data['opened_on']})" if data.get("opened_on") else ")"
        text += f". {len(notices)} notice(s)"
        text += f", notices covered since {since}." if since else "."
        if state == "none_found":
            text += " No notice in the years covered is not proof that there was no procedure."
        yield self.create_text_message(text)
        yield self.create_json_message(answer)
        yield self.create_variable_message("state", state)
        yield self.create_variable_message("procedure", str(procedure or ""))
        yield self.create_variable_message("covered_since", since)
