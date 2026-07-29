# Collection safety and scope

## Allowed boundary

Collect only information that an authorized user can ordinarily view. Respect applicable law, platform terms, copyright, privacy, robots controls, rate limits, and organizational policy. Public visibility does not automatically authorize unrestricted reuse or publication.

## Human-in-the-loop events

Pause and ask the user to act when a site presents CAPTCHA, identity verification, consent, login recovery, account-security prompts, or a decision that could change external state. Never simulate or bypass the human check.

## Browser and credential hygiene

Use a dedicated research browser profile when browser-backed collection is necessary. Log into only the platforms required for the declared run; do not use the same profile for corporate email, finance, HR, source control, or collaboration systems.

- Keep credentials in the browser's normal local profile rather than CSV files, source control, prompts, screenshots, or report artifacts.
- Prefer public unauthenticated access when it satisfies the research contract.
- Treat extensions with browser-debugging, cookie, or all-site permissions as privileged software. Pin a reviewed version, keep the extension updated, and disable it when it is not needed.
- Record the access method, automation tool/version, delay or rate controls, and whether human verification was encountered in `run_manifest.json`.
- Stop the run on repeated access errors, unexpected account-security prompts, or any indication that continuing would violate the declared scope.

## Coverage language

Use “in-scope public corpus” or “best-effort census at the cutoff.” Record:

- target and verified account identity;
- included platforms and date range;
- cutoff timestamp and collection timezone;
- visible totals versus captured totals;
- unavailable, deleted, duplicated, or restricted items;
- authentication state and known personalization effects;
- collection controls and any human intervention;
- sampling rule for comments, if comments are not exhaustively captured.

## Publication checklist

Before sharing a repository or report, remove credentials, cookies, session IDs, private URLs, personal contact details, real customer usernames, internal recommendations, employer/client names, and proprietary source data. Prefer fictional demo data. A fresh repository history is safer than deleting sensitive files from an existing history.
