from collections.abc import Generator
from typing import Any

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools.fuentio_client import call, clean, country_code, name_of, primary_id, status_of


class SearchCompaniesTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        country = country_code(tool_parameters.get("country"))
        query = str(tool_parameters.get("query") or "").strip()
        page = tool_parameters.get("page")
        answer = call(
            self.runtime.credentials["fuentio_api_key"],
            "GET",
            "/v1/companies/search",
            params=clean(
                {
                    "country": country,
                    "q": query,
                    "postal_code": tool_parameters.get("postal_code"),
                    "locality": tool_parameters.get("locality"),
                    "status": tool_parameters.get("status"),
                    "page": int(page) if page else None,
                }
            ),
        )
        rows = answer.get("data") or []
        meta = answer.get("meta") or {}
        if not rows:
            text = f"No company found for '{query}' in {country}."
        else:
            lines = [
                f"{n}. {name_of(c)} — {country} {primary_id(c)} — {status_of(c)}"
                + (f" (match {m.get('score')}, {m.get('band')})" if (m := c.get("match")) else "")
                for n, c in enumerate(rows, 1)
            ]
            more = f" Next page: {meta['next_page']}." if meta.get("next_page") else ""
            text = (
                f"{len(rows)} companies for '{query}' in {country} (page {meta.get('page', 1)}, "
                f"{meta.get('total', len(rows))} in all), best match first:\n"
                + "\n".join(lines)
                + f"\nUse an ID with lookup_company or verify_company.{more}"
            )
        yield self.create_text_message(text)
        yield self.create_json_message(answer)
