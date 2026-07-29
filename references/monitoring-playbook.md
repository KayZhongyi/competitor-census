# Material-change monitoring

Use this playbook when the question changes from “what is the public footprint at a cutoff?” to “what changed that a business owner should review?”

## Define a watch contract

For every watch, record the target, verified accounts or URLs, platform, market, time zone, collection frequency, time window, source boundary, owner, approved destination, and stop condition. Start with a small, fixed watchlist; do not turn open-ended keyword search into an unattended alert stream.

## Establish a baseline

Run a full in-scope census first. Preserve its raw bundle, manifest, report, and analysis outputs. Every subsequent run goes into a new dated directory and merges against the baseline or latest approved bundle by stable ID.

## Classify changes before alerting

`merge_incremental.py` records `new`, `updated`, `unchanged`, and `absent_from_incoming` records. Updated records include changed fields and change kinds:

- `content`: text, translation, category, or topic changed;
- `engagement`: views, likes, comments, or shares changed;
- `metadata`: another source field changed.

Default rules:

- alert a new publication, new public product/price/support statement, or material content change;
- summarize engagement movement only when it crosses a business-defined threshold or changes a ranking decision;
- never alert an absent record as a deletion without source verification;
- human-review any high-severity customer signal, identity uncertainty, or low-confidence classification.

## Send an evidence-linked brief

Use one brief per material change:

```text
Change: [new content / material content change / threshold-crossing signal]
Observation: [fact with n/N or before/after values]
Evidence: [record ID and source URL]
Interpretation: [cautious, optional]
Requested review: [owner and decision]
Scope: [platform, cutoff, known limitations]
```

Do not paste raw session material, personal data, or a whole unreviewed corpus into an alert. See [collaboration-handoff.md](collaboration-handoff.md) for Feishu or Bitable delivery.
