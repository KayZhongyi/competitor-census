<p align="center">
  <img src="assets/hero.svg" alt="Competitor Census — public signals to traceable strategy" width="100%" />
</p>

<p align="center">
  <a href="https://github.com/KayZhongyi/competitor-census/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/KayZhongyi/competitor-census/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-D49A43.svg"></a>
  <a href="https://github.com/KayZhongyi/competitor-census/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/KayZhongyi/competitor-census?style=flat"></a>
  <a href="README.zh-CN.md">中文</a>
</p>

**Turn any competitor's public footprint into a traceable intelligence dossier.**

Competitor Census is a reusable Agent Skill and open toolkit for global competitor research. Give it a company and market; it helps discover the channels that matter, build a structured evidence base, translate multilingual content, derive categories from the real corpus, quantify what performs, and generate a report whose claims lead back to source rows and URLs. The same evidence bundle can run a validated customer-voice analysis when public conversations are available.

> Census first. Conclusions second.

## What it does

| Capability | Result |
|---|---|
| **Platform census** | Find and verify the competitor's active public channels before choosing where to go deep |
| **In-scope capture** | Preserve publication dates, text, views, likes, comments, shares, account fields, and source URLs |
| **Multilingual normalization** | Keep original text beside a separate working translation in one consistent schema |
| **Corpus-grounded classification** | Let an Agent read the complete corpus and derive categories from repeated meanings rather than preset keywords |
| **Professional analysis** | Compare content supply with mean and median reach, count customer needs, study reply patterns, and map opportunities |
| **Customer voice mode** | Derive issue categories, classify intent/sentiment/severity, link visible official replies, and redact public usernames in shareable output |
| **Traceable delivery** | Produce CSV evidence, a declared taxonomy, validation results, and an evidence-linked HTML report |

The same workflow can be reused across companies, languages, regions, and approved collection tools because the evidence schema and analysis layer stay independent from the source platform.

## See it in 60 seconds

No API key, browser login, or package install is required:

```bash
git clone https://github.com/KayZhongyi/competitor-census.git
cd competitor-census
python3 scripts/run_demo.py
```

Open `demo/output/report.html`, or view the [live fictional report](https://kayzhongyi.github.io/competitor-census/).

<p align="center">
  <img src="assets/demo-preview.svg" alt="Fictional evidence-linked competitor report preview" width="100%" />
</p>

## Run a real public-channel census

The included YouTube connector captures public video metadata without downloading media. Start with a small verification run:

```bash
python3 -m pip install -U "yt-dlp[default]"
python3 scripts/collect_youtube.py \
  --company "OpenAI" \
  --channel "https://www.youtube.com/@OpenAI" \
  --tabs videos \
  --max-items-per-tab 10
```

It writes the evidence bundle, baseline report, run manifest, and an Agent-ready analysis packet to `runs/openai/`.

<p align="center">
  <img src="assets/youtube-live-demo.gif" alt="YouTube public metadata collection to evidence bundle and report" width="100%" />
</p>

After checking the account and fields, run a best-effort census of all retrievable entries in the selected tabs:

```bash
python3 scripts/collect_youtube.py \
  --company "Target Company" \
  --channel "https://www.youtube.com/@TargetHandle" \
  --tabs videos,shorts,streams \
  --max-items-per-tab 0
```

For repeat monitoring, collect a date-bounded update into a new directory and merge by stable ID:

```bash
python3 scripts/collect_youtube.py \
  --company "Target Company" \
  --channel "https://www.youtube.com/@TargetHandle" \
  --since 2026-07-01 \
  --output runs/target-2026-07

python3 scripts/merge_incremental.py \
  --base runs/target-baseline/content.csv \
  --incoming runs/target-2026-07/content.csv \
  --output runs/target-current/content.csv
```

The merge report separates new, updated, unchanged, and absent-from-this-run records without treating absence as deletion.

## Complete the analysis with any Agent

Each collection run creates a model-agnostic task at `analysis/analysis_task.md`. Ask your preferred file-capable Agent to follow it, then validate the completed work:

```text
Use $competitor-census to follow runs/openai/analysis/analysis_task.md.
Read the complete corpus, derive the taxonomy, and fill every analysis row.
```

```bash
python3 scripts/apply_analysis.py --bundle runs/openai
```

```text
content.csv (source evidence, unchanged)
  → Agent reads the complete corpus
  → taxonomy.json + analysis_results.csv
  → deterministic validation
  → analyzed_content.csv + analysis_report.html
```

The validator checks the source fingerprint, exact ID coverage, translation completeness, category definitions, confidence values, and representative evidence before producing the analyzed dataset and report.

## Run customer voice analysis

When an evidence bundle contains public conversations in `comments.csv`, create an independent customer-voice task:

```bash
python3 scripts/prepare_customer_voice.py --bundle runs/target-company
```

Ask any file-capable Agent to follow `voice/voice_task.md`, then validate and render:

```bash
python3 scripts/apply_customer_voice.py --bundle runs/target-company
```

```text
comments.csv + content.csv (source evidence, unchanged)
  → Agent reads the complete customer corpus
  → voice_taxonomy.json + voice_results.csv
  → deterministic validation + official-reply linking
  → analyzed_voice.csv + customer_voice_report.html
```

The mode separates **issue**, **intent**, **sentiment**, and **severity** instead of reducing customer feedback to a positive/negative score. High-severity records require visible justification, and the shareable report replaces public usernames with stable aliases.

## Install as an Agent Skill

### Codex

```bash
git clone https://github.com/KayZhongyi/competitor-census.git ~/.codex/skills/competitor-census
```

### Claude Code

```bash
git clone https://github.com/KayZhongyi/competitor-census.git ~/.claude/skills/competitor-census
```

Then ask:

```text
Use $competitor-census to research the public channels of [company] in [market].
Build the evidence bundle first, then write a traceable strategy report.
```

The Skill is plain Markdown plus Python standard-library tooling, so other terminal- and browser-capable Agents can use the same workflow.

## What you get

| Artifact | Purpose |
|---|---|
| `platform_census.csv` | Audited accounts, identity evidence, activity, and deep-dive decisions |
| `content.csv` | Source-level public content and point-in-time metrics |
| `comments.csv` | Public conversation evidence and official-reply structure when collected |
| `run_manifest.json` | Scope, cutoff, tools, coverage, and collection record |
| `analysis/taxonomy.json` | Corpus-derived category definitions and representative row IDs |
| `analysis/validation_report.json` | Machine-checkable completeness and integrity result |
| `analyzed_content.csv` | Translation and classification merged without changing source evidence |
| `analysis_report.html` | Management-ready findings with counts, denominators, evidence IDs, and source links |
| `voice/voice_taxonomy.json` | Corpus-derived customer-issue definitions and representative comment IDs |
| `voice/validation_report.json` | Completeness, integrity, and labeling checks for customer voice |
| `analyzed_voice.csv` | Validated customer signals with redacted author aliases and visible-response linkage |
| `customer_voice_report.html` | Issue, intent, sentiment, severity, response, and evidence-led customer voice report |

## Analysis built for decisions

- **Emergent taxonomy:** categories come from the corpus instead of a rigid template.
- **Coverage–performance gap:** publishing share is compared with both mean and median reach.
- **Voice of customer:** concrete needs are counted with visible denominators.
- **Customer signal triage:** issue, intent, sentiment, severity, and confidence remain separate.
- **Response-pattern analysis:** useful answers, templates, redirection, and silence are separated.
- **Opportunity mapping:** high-demand/low-supply themes become testable content and service opportunities.
- **Evidence thresholds:** small or ambiguous samples remain labeled instead of becoming confident prose.

See [`references/analysis-playbook.md`](references/analysis-playbook.md) for competitor analysis, [`references/customer-voice-playbook.md`](references/customer-voice-playbook.md) for customer voice, and [`references/research-modes.md`](references/research-modes.md) for mode selection.

## Designed for trustworthy reuse

- Raw evidence stays separate from translation, classification, and conclusions.
- Stable IDs and source links make every important number auditable.
- Input fingerprints prevent an old analysis from being applied to a changed corpus.
- Shareable customer-voice outputs replace public usernames with stable aliases.
- Human review remains at account verification, platform challenges, and final business judgment.
- Standard CSV/JSON contracts make new approved connectors and report formats easy to add.
- Date-bounded capture and stable-ID merging support repeat monitoring without overwriting earlier evidence.

Responsible collection guidance lives in [`references/collection-safety.md`](references/collection-safety.md). The included demo is entirely fictional and public-safe.

Contributions are welcome, especially approved connectors, analysis methods, and report themes. See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE)
