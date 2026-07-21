---
name: competitor-census
description: Build an evidence-backed competitor intelligence dataset and report from publicly visible web and social channels. Use when an agent must discover a competitor's real active platforms, capture in-scope public content without relying on a small sample, translate multilingual material, analyze content performance and customer questions, preserve source-level traceability, or repeat the same research workflow for another company or market.
---

# Competitor Census

Turn scattered public competitor signals into two separate deliverables: a machine-readable evidence bundle and a decision-ready report. Treat a census as a best-effort capture of all in-scope, publicly visible records at a stated cutoff—not as a guarantee about hidden, deleted, personalized, or access-restricted content.

## Non-negotiable boundaries

- Work only with information visible through authorized, ordinary access.
- Never bypass authentication, CAPTCHA, rate limits, robots controls, or platform safeguards.
- When a human-verification challenge appears, pause, notify the user, and resume only after the user completes it.
- Keep raw evidence separate from translation, classification, and conclusions.
- Record scope, cutoff time, failures, and coverage limitations. Do not call a dataset “complete” without those qualifiers.
- Do not publish personal data, credentials, private URLs, client names, internal strategy, or proprietary datasets.

Read [references/collection-safety.md](references/collection-safety.md) before live collection.

## Workflow

### 0. Define the research contract

Capture the target company, market, known handles/domains, business questions, public-source boundary, time cutoff, desired output, and allowed tools. Create a run directory and never mix targets.

### 1. Census platforms before choosing depth

Check likely channels such as the company website, TikTok, Facebook, YouTube, Instagram, LinkedIn, X, Telegram, and local platforms. Do not assume the most familiar platform is the most important one.

For every candidate account, record:

- platform, handle, URL, follower/subscriber count, post count, last activity, and collection decision;
- identity evidence from language, address, phone/domain, cross-links, and branding;
- any same-name collision or uncertainty.

Deep-dive all channels that the census shows are materially active. Multiple platforms may qualify.

### 2. Capture the in-scope public corpus

Collect all retrievable records inside the declared scope. Preserve source fields before adding interpretation:

- stable record ID, platform, account, published date/time, original text, canonical URL;
- views/plays, likes, comments, shares, and other platform-native interactions;
- media type and any visible product/brand references;
- collection timestamp and retrieval status.

Use incremental capture for virtualized or infinite-scroll pages. Deduplicate by stable ID or canonical URL, not by text alone. Normalize Unicode before matching disguised phone numbers or product codes. See [references/data-schema.md](references/data-schema.md).

### 3. Deep-read high-value conversations

Rank content using reach, comment volume, recency, and strategic relevance, then capture publicly visible comments and official replies from the chosen set. If useful comments are sparse, widen the content set and say so explicitly; never inflate a thin sample.

Classify commenter identity only when the text supports it: end customer, installer/DIY, reseller, or EPC/project party. If a group has fewer than three credible records, state “sample too small; not reported separately.” Determine official replies by exact account identity or an explicit creator/author marker.

### 4. Normalize and translate

Preserve original text, write translation to a separate field, and retain platform-specific metrics. Remove invalid surrogate characters before CSV or document output. Validate required columns, unique IDs, URLs, numeric fields, and source-to-translation row counts.

### 5. Analyze from evidence upward

Read [references/analysis-playbook.md](references/analysis-playbook.md). Apply these methods:

1. **Emergent taxonomy:** derive content and customer-need categories from the corpus; do not force records into preset labels.
2. **Coverage–performance gap:** compare publishing share with median and mean reach/engagement by category.
3. **Voice-of-customer frequency:** count concrete questions and pain points, with denominators.
4. **Response-pattern analysis:** quantify which questions receive a useful answer, a template reply, redirection, or no visible reply.
5. **Opportunity mapping:** identify high-demand/low-supply topics and observable information gaps.
6. **Evidence thresholds:** attach `n/N` to claims and mark small samples or ambiguous identity.

Describe the competitor as the subject. Prefer “36 of 187 user comments asked about price” over “36 hits.” Separate observation, inference, and recommendation.

### 6. Produce two deliverables

First finalize the evidence bundle:

- `platform_census.csv`
- `content.csv`
- `comments.csv`
- `run_manifest.json`

Then independently write the report:

- one-page executive brief;
- what the competitor publishes;
- what customers ask;
- what content performs;
- response behavior and public information gaps;
- implications and recommended tests;
- scope, cutoff, limitations, and evidence links.

Every quantitative claim must link back to row IDs or source URLs. Keep non-Latin original text in the evidence bundle unless the requested report font is verified to support it.

### 7. Quality gate

Before delivery, verify:

- target identity and same-name collisions;
- unique row counts and coverage by platform;
- dates, engagement metrics, translations, and source URLs;
- official-reply logic and commenter-identity confidence;
- arithmetic and denominators behind every claim;
- raw-data/report separation;
- removal of secrets, private data, and unsupported certainty.

## Offline demo

Run the repository demo without API keys or browser access:

```bash
python3 scripts/run_demo.py
```

It validates a fictional evidence bundle and generates an evidence-linked HTML report plus JSON summary. Use it to confirm the workflow before connecting live collection tools.
