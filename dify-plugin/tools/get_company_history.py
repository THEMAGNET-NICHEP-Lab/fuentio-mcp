from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.fuentio_client import call, clean, company_path


class GetCompanyHistoryTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        page = tool_parameters.get("page")
        answer = call(
            self.runtime.credentials["fuentio_api_key"],
            "GET",
            company_path(
                tool_parameters.get("country"), tool_parameters.get("identifier"), "/history"
            ),
            params=clean(
                {"id_scheme": tool_parameters.get("id_scheme"), "page": int(page) if page else None}
            ),
        )
        data = answer.get("data") or {}
        meta = answer.get("meta") or {}
        versions = data.get("snapshots") or []
        events = data.get("events") or []
        name = data.get("name") or data.get("company_id") or ""
        text = f"{name}: {len(versions)} version(s) and {len(events)} dated event(s) on this page"
        if meta.get("history_since"):
            text += f"; history since {meta['history_since']}"
        text += "."
        if meta.get("next_page"):
            text += f" Next page: {meta['next_page']}."
        yield self.create_text_message(text)
        yield self.create_json_message(answer)
