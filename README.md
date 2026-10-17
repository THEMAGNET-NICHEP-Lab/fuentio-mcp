# Fuentio: UK, France & Spain company data from official registries

**Verify UK, French and Spanish companies from official registries, with source, check date and receipt on every answer.**

Fuentio gives AI agents and compliance teams clean company data for the United Kingdom, France and Spain, straight from official sources: Companies House for the UK (every company, with insolvency cases, charges and latest filings), INSEE Sirene and the national register for France, BORME (Registro Mercantil acts since 2009) for Spain, and GLEIF for LEIs and group links. Every answer carries the source, link, check date and a receipt you can show an auditor. Connect with just the URL; free tier, no card.

```
https://api.fuentio.com/mcp
```

Ask your agent "Verify the UK company 00445790 for onboarding.", "Which company is behind this
SIREN?" or "¿Sigue activa esta sociedad según el BORME?" and get an answer you can trust and prove.

## What you get

- UK company lookup, search and verification from Companies House (company number or name), including dissolved companies, insolvency cases, charges and latest filings.
- Company lookup and search for France (SIREN, SIRET, name) and Spain (company name, BORME acts
  since January 2009).
- One record per real company, matched across registers and GLEIF, with the reason for every
  match and every non-match.
- Company group links (parent and subsidiary companies reported to GLEIF).
- Company history: what changed and when.
- A `verify_company` check for onboarding (KYB): status, address, identifiers and evidence in
  one call.
- Insolvency notices (BODACC for France, BORME for Spain).
- Sanctions list screening with clear coverage notes.
<!-- [if live] keep the next line only if watch_company passed its launch-day checks -->
- Change alerts with `watch_company`.

## Why agents pick it

- Official sources only, never scraped guesses.
- Every answer includes the source, a link, the check date, an uncertainty label and a receipt
  id.
- When sources disagree, you see both values, never a silent pick.
- Short answers by default, errors that say exactly what to retry.

## Install

**Claude Code**

```bash
claude mcp add --transport http fuentio https://api.fuentio.com/mcp
```

**Claude Desktop / claude.ai:** Settings → Connectors → Add custom connector → paste
`https://api.fuentio.com/mcp`.

**Cursor / VS Code / any client (JSON),** as in this repository's [`mcp.json`](mcp.json):

```json
{ "mcpServers": { "fuentio": { "url": "https://api.fuentio.com/mcp" } } }
```

VS Code's own `.vscode/mcp.json` format:

```json
{ "servers": { "fuentio": { "type": "http", "url": "https://api.fuentio.com/mcp" } } }
```

**Gemini CLI:** `gemini extensions install <this repository's URL>` (it reads
[`gemini-extension.json`](gemini-extension.json)).

**Cline:** ask Cline to install this server; it follows [`llms-install.md`](llms-install.md).

**ChatGPT (developer mode):** create a connector with the URL above, no authentication.

**With a key** (paid plans, or a free key for the tools marked "key" below):

```json
{ "mcpServers": { "fuentio": { "url": "https://api.fuentio.com/mcp", "headers": { "Authorization": "Bearer YOUR_KEY" } } } }
```

A free key (100 units a month, one per person) takes under a minute:
`curl -X POST https://api.fuentio.com/v1/keys -H "Content-Type: application/json" -d '{"email":"you@example.com"}'`. The key arrives by email.

## Tools

| Tool | What it does | Cost |
|---|---|---|
| `list_coverage` | Countries, ID formats and official sources covered | free |
| `lookup_company` | A company by official ID: UK company number (e.g. `00445790`); France SIREN (9 digits), SIRET (14), VAT; Spain Registro Mercantil sheet (e.g. `VI-23266`) | 1 unit |
| `search_companies` | Find a company by name, 10 per page | 2 units |
| `get_company_history` | What changed at a company, and when, each change with its source | 1 unit |
| `verify_company` | Onboarding (KYB) check: outcome with reasons, warning signals, receipt | 5 units |
| `get_receipt` | The Fuentio receipt of a verification by proof code, normal or detailed (public view unless your key ran the check) | free |
| `resolve_company` | Is this the same company? Candidates with evidence, from an ID or a name and town | 2 units |
| `explain_match` | Why two records are, or are not, the same company | 1 unit |
| `get_evidence` | Every value behind a company's facts, each with its source and date | 1 unit |
| `what_changed` | What changed at a company since a date, across all its records | 1 unit |
| `get_graph` | A company's group: GLEIF parents and subsidiaries, every link with its source (key) | 2 units |
| `check_insolvency` | Insolvency notices: BODACC (France), BORME insolvency acts (Spain) | 1 unit |
| `screen_company` | The company's own names against the EU, UK, OFAC and French sanctions lists (key) | 2 units |
| `check_address` | A French company's registered address against the Base Adresse Nationale | 1 unit |
| `check_vat` | A French company's EU VAT number, with a link to check it on VIES | 1 unit |
| `review_report` | One review-ready report: identity, facts with sources, changes, every check (key) | 8 units |
| `watch_company` | Signed webhooks when a company's official records change (key) | 1 unit |
| `report_issue` | Report an answer you believe is wrong, so it is checked against the source (key) | free |

Prompt: `check_a_company(country, name_or_id)` finds and verifies a company, then answers in one
paragraph with the outcome, source, check date and receipt.

## Sources

- **United Kingdom:** Companies House (its public data API and free monthly company file), with
  insolvency cases, charges and latest filings. Contains public sector information licensed under
  the Open Government Licence v3.0.
- **France:** INSEE Sirene and the Registre national des entreprises, through the Annuaire des
  Entreprises; BODACC; Base Adresse Nationale. Licence Ouverte / Etalab 2.0.
- **Spain:** BORME, the Registro Mercantil gazette published by the Agencia Estatal Boletín
  Oficial del Estado (https://www.boe.es).
- **All three:** GLEIF (LEIs and parent links, CC0); the EU, UK, OFAC and French sanctions lists.

## Limits

- Keyless trial: 20 units a day. Free key: 100 units a month. Paid plans:
  https://fuentio.com/pricing/
- UK, France and Spain only. No Spanish NIF/CIF lookup, no full financial statements, no data about people (no UK officers or PSCs).
- Spain covers companies with an act published in BORME since 2 January 2009, not every Spanish
  company: search Spanish companies by name.
- No beneficial owners and no credit scores.
- Fuentio does not check VAT registration: `check_vat` gives the number and links VIES.

## Licence

The documentation and install snippets in this repository are MIT-licensed. The Fuentio service
and its data are governed by the terms at https://fuentio.com and the sources' licences above.

Contact: hello@fuentio.com
