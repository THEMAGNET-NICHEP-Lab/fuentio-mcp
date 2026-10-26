# Fuentio for Dify

Check companies in official registers from your Dify agents and workflows: France (Annuaire des
Entreprises: INSEE Sirene and RNE; BODACC), the United Kingdom (Companies House) and Spain (BORME,
the Registro Mercantil gazette). Every answer cites its official source and the date Fuentio
checked it.

A registry check is not full KYB, UBO proof or sanctions clearance.

## Tools

| Tool | What it does | Units |
|---|---|---|
| `search_companies` | Find companies by name, 10 per page, best match first with a match score. Use an ID from the results with the other tools. | 2 a page |
| `lookup_company` | One company by official ID: status, address, legal form, activity, source and check date. | 1 |
| `verify_company` | A registry check before onboarding, paying or signing: an outcome (verified, partial, unverified) with reasons and a proof code (FUE-…) stored 24 months. An open insolvency is never verified. | 5 (1 if not found) |
| `check_insolvency` | Insolvency notices and state: France from BODACC (since 2008), Spain from BORME insolvency acts. | 1 |
| `get_company_history` | What changed at a company, and when, each change with its official source. | 1 |

Official IDs: France SIREN (9 digits), SIRET (14) or VAT (FR + 11); United Kingdom company
number (e.g. 00445790); Spain Registro Mercantil sheet (e.g. VI-23266); or an LEI. With only a
name, call `search_companies` first.

## Setup

1. Install **Fuentio** from the Dify Marketplace (or upload the `.difypkg` under
   Plugins → Install plugin → Local package file).
2. Get your own Fuentio API key: a free key (100 units a month, one per person) takes a minute
   at [fuentio.com](https://fuentio.com/pricing/); paid plans add units. The plugin has no
   shared key: every call is made with, and charged to, the key you enter.
3. In Dify, open Plugins → Fuentio → **Authorize** and paste the key. The plugin checks it with
   a free call (`GET /v1/usage`).

## Usage

**In an agent or chatflow:** add the Fuentio tools. The tool descriptions tell the model when to
use each one (for example: search by name, then verify with the ID found).

**In a workflow:** add a Fuentio tool node and map its inputs (`country`, `identifier`,
`query`). Each tool returns:

- `text`: one readable line (e.g. "CAMAIEU INTERNATIONAL (FR 345086177): unverified
  (insolvency_liquidation). Proof code FUE-FR-…");
- `json`: the full Fuentio answer (`data` and `meta`, with source, source URL and check date);
- variables to branch on: `verify_company` gives `outcome`, `reasons`, `proof_code`,
  `company_name` and `checked_at`; `lookup_company` gives `company_name`, `official_id`,
  `status`, `source` and `checked_at`; `check_insolvency` gives `state`, `procedure` and
  `covered_since`.

Example: an If/Else node on `verify_company.outcome == "verified"` routes a new supplier to
approval, and anything else to a manual review with the reasons and the proof code.

## Coverage and limits

- **France:** every company in the public Sirene directory, from the official Annuaire des
  Entreprises (INSEE Sirene, RNE). Insolvency notices from BODACC since 2008. "Ceased" (cessée)
  is not a legal dissolution.
- **United Kingdom:** Companies House. No officers or persons with significant control; figures
  only from accounts filed electronically.
- **Spain:** companies with an act published in BORME since 2 January 2009. No NIF/CIF lookup
  (search by name instead). Status is `unknown` unless an act says otherwise.
- **No person's name in any answer:** directors, shareholders and sole traders are not served.
- Other countries are not covered: the tools accept FR, GB and ES only.

## Connection requirements

The plugin connects only to `https://api.fuentio.com` (HTTPS, port 443), with a 30-second
timeout per call. The key is sent in the `X-API-Key` header and never appears in errors or
answers. Your Dify instance needs outbound internet access to that host.

## Privacy

See [PRIVACY.md](PRIVACY.md) and Fuentio's policy at https://fuentio.com/legal/privacy/.

## Support

- Email: hello@fuentio.com
- Source: https://github.com/THEMAGNET-NICHEP-Lab/fuentio-mcp/tree/main/dify-plugin
- API documentation: https://api.fuentio.com/docs

## Development

Python 3.12. Install `requirements.txt` plus `pytest` and `responses`, then run `pytest` from
this folder (the Fuentio API is mocked; no key needed). Package with
`dify plugin package ./dify-plugin`.

## Changelog

- **0.0.1:** first version: search, lookup, verify, insolvency and history for France, the
  United Kingdom and Spain.
