# Collaboration handoff

Use collaboration tools to shorten the path from reviewed evidence to a business decision. Do not use them as a substitute for the raw evidence bundle or its validation record.

## Architecture

```text
Access-controlled evidence bundle
  -> reviewed evidence index
  -> decision brief / action owner
  -> feedback into the next capture or analysis run
```

Keep the complete raw CSV/JSON files, source text, collection manifest, and validation report in a controlled folder or approved repository. The collaboration layer contains only the fields needed to understand, verify, assign, and close a business action.

## Minimum reviewed-evidence fields

Use these fields in a Bitable, spreadsheet, issue tracker, or equivalent system:

- `evidence_id`: stable source record or aggregate finding ID;
- `research_mode`: competitor intelligence or customer voice;
- `platform`, `published_at`, and `market`;
- `finding`: factual observation with `n/N` when aggregated;
- `translation_or_summary`: reviewed working-language text, not an AI conclusion presented as source text;
- `category_or_issue`, `confidence`, and `severity` when applicable;
- `source_url`: direct source link, subject to access rights;
- `recommended_review`: proposed human decision or experiment;
- `owner`, `status`, `updated_at`, and `run_id`.

Do not include cookies, tokens, private URLs, raw usernames, phone numbers, addresses, or the entire unreviewed corpus.

## Feishu pattern

1. Import or write the reviewed evidence index to a private Feishu Bitable. Create at least three views: `content performance`, `customer signals`, and `needs review`.
2. Send a concise group card only when there is a material change. Include the change, its denominator, the proposed owner/action, and a link to the Bitable or report.
3. Let the owner record the decision or experiment in the Bitable. Feed the result into the next periodic run.

For a manual pilot, import an approved CSV into a private Bitable and send the first card manually. Describe this as an internal collaboration pilot.

For an automated production flow, use an approved self-built Feishu app. It needs a defined destination, least-privilege permissions, an app bot in the target group, and secrets kept outside the repository. Feishu's record-create API requires an authorized tenant or user token and edit permission; the message API requires an enabled bot with group permission. Use a deduplication ID for card sends and respect rate limits.

## Example group brief

```text
New public signal | 2026-08-15
Observation: 12 of 54 captured customer questions this period concerned installation compatibility.
Evidence: CV-20260815-12 to CV-20260815-23, reviewed in the Bitable.
Suggested review: Presales owner to confirm whether an installation FAQ or technical response is needed.
Status: awaiting review
```

## Handoff checks

- The summary links to a reviewed evidence ID and source URL.
- The scope, cutoff, and denominator remain visible.
- Observation, inference, and recommended action are separate fields.
- High-severity or low-confidence items require human review before escalation.
- The raw evidence bundle remains immutable and access-controlled.
- No live integration is described as deployed until the app permissions and destination have been verified.
