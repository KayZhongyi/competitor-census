# Evidence bundle schema

Keep raw source fields immutable. Add translations and analysis fields in separate columns.

## `platform_census.csv`

| Field | Meaning |
|---|---|
| `platform` | Channel or website |
| `handle` | Account identifier |
| `url` | Canonical account URL |
| `identity_status` | verified / probable / rejected / unresolved |
| `identity_evidence` | Language, address, domain, phone, or cross-link evidence |
| `followers` | Visible audience count |
| `visible_items` | Visible content count |
| `last_active_at` | Most recent visible activity |
| `deep_dive` | yes / no / pending |
| `notes` | Limits and ambiguity |

## `content.csv`

Required demo fields:

| Field | Meaning |
|---|---|
| `record_id` | Stable local or platform ID |
| `platform` | Source platform |
| `account` | Verified source account |
| `published_at` | ISO 8601 date/time when available |
| `language` | Original language code/name |
| `text_original` | Unmodified visible text |
| `text_translation` | Separate working translation |
| `views` | Plays/views, blank if unavailable |
| `likes` | Likes/reactions |
| `comments_count` | Visible comment count |
| `shares` | Shares/reposts, blank if unavailable |
| `url` | Source URL |
| `content_type` | Emergent category assigned after capture |
| `brand` | Visible promoted brand/product |

Production bundles should also include `collected_at`, `retrieval_status`, `media_type`, and `classification_notes`.

## `comments.csv`

| Field | Meaning |
|---|---|
| `comment_id` | Stable comment ID |
| `content_id` | Parent content record |
| `parent_comment_id` | Parent comment when this is a reply |
| `commenter` | Public display identifier; redact before publication |
| `commenter_type` | end_customer / installer_diy / reseller / epc_project / unknown |
| `is_official` | true only after deterministic identity check |
| `text_original` | Unmodified visible text |
| `text_translation` | Separate working translation |
| `likes` | Visible likes |
| `topic` | Emergent customer-need topic |
| `response_mode` | useful_answer / template / redirect / no_reply / not_applicable |
| `url` | Source URL |

## `run_manifest.json`

Record target, market, cutoff, timezone, platforms checked, included scope, comment selection rule, tool versions, row counts, validation results, failures, and known limitations.
