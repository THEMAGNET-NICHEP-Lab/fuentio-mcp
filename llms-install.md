# Installing the Fuentio MCP server

Fuentio is a **remote** MCP server. There is nothing to download, build or run locally: add the
URL to the client's MCP settings.

- URL: `https://api.fuentio.com/mcp`
- Transport: streamable HTTP
- Authentication: none needed to start (keyless trial, 20 units a day). An API key is optional.

## Steps

1. Open the MCP settings file of the client (for Cline: `cline_mcp_settings.json`).
2. Add this entry under `mcpServers`, keeping any servers already there:

   ```json
   {
     "mcpServers": {
       "fuentio": {
         "type": "streamableHttp",
         "url": "https://api.fuentio.com/mcp",
         "disabled": false
       }
     }
   }
   ```

3. Save. The client connects and lists the tools.
4. Check it works: call `list_coverage` (free, no key). It returns the covered countries (the
   United Kingdom, France and Spain), the ID formats and the official sources.

## Optional: an API key

Some tools (`get_graph`, `screen_company`, `review_report`, `watch_company`, `report_issue`) and
anything beyond the trial need a key. Ask the user to create one themselves; never create, print
or store a key on their behalf.

- Free key (100 units a month, one per person, email required): the user runs
  `curl -X POST https://api.fuentio.com/v1/keys -H "Content-Type: application/json" -d '{"email":"you@example.com"}'`; the key arrives by email.
- Paid plans: https://fuentio.com/pricing/

The user then adds the header to the same entry:

```json
"headers": { "Authorization": "Bearer YOUR_KEY" }
```

## Notes for the agent

- Start with `list_coverage` when unsure whether a country or ID is covered.
- With a name and no official number, call `search_companies`, then use an ID from the results.
- Spanish NIF/CIF numbers are not supported: search Spanish companies by name.
- Quote the source and check date from every answer.

Support: hello@fuentio.com
