# Privacy policy: Fuentio plugin for Dify

Last updated: 26 October 2026. Contact: hello@fuentio.com.

## What the plugin sends, and to whom

When a Fuentio tool runs, the plugin sends a request over HTTPS to one external service only:
Fuentio's API at `https://api.fuentio.com`. The request carries:

- your Fuentio API key (in the `X-API-Key` header), which identifies your account;
- the tool's inputs: the country, the company's official ID or the company name searched, and,
  when you give them, a postal code, a town, a status filter, a page number, an ID type and,
  for `verify_company`, your own reference.

The plugin sends nothing else and to no one else. (Fuentio's API is served through Cloudflare,
Fuentio's network provider, as its privacy policy explains.)

## What the plugin stores or logs

Nothing. The plugin keeps no data between calls and writes no logs of its own. Your API key is
stored by Dify as an encrypted credential of your workspace, like any other plugin credential.

## What Fuentio does with a request

Fuentio is the third party that receives the request. Under its privacy policy
(https://fuentio.com/legal/privacy/):

- each call is counted against your API key for usage and billing;
- `verify_company` results, with your reference, are kept for 24 months so that the proof code
  can be checked later;
- to answer, Fuentio may ask the official source (Annuaire des Entreprises in France, Companies
  House in the United Kingdom) for the company by its ID or name.

## Personal data

The tools are about companies. Answers come from official company registers and contain no
person's name: directors, shareholders and sole traders are not served. Search by company names
and IDs only, and do not put personal data in the `reference` field.

## Your rights

To ask about, access or delete data linked to your API key, write to hello@fuentio.com.
