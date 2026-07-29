# Customer voice playbook

## 1. Define the signal population

Declare the brand, product, issue or query; market and language; included platforms/accounts; date range; cutoff; and whether the corpus covers account comments, cross-account mentions, reviews, or a defined combination.

Do not describe public comments as representative of all customers. Use “captured public customer signals” and retain the denominator.

## 2. Derive the issue taxonomy

Read all non-official signals before naming issues. Group repeated meanings, define boundaries, review ambiguous records, and merge categories that are too small or indistinguishable. Preserve representative comment IDs.

Do not begin with a fixed list such as price, installation, warranty, or support. Those categories are valid only when they emerge from the corpus.

## 3. Separate the analysis dimensions

- **Issue:** what subject or problem is visible?
- **Signal type:** question, complaint, request, praise, experience, or other.
- **Sentiment:** positive, neutral, negative, mixed, or unclear.
- **Severity:** informational, low, medium, high, or critical.
- **Confidence:** how clearly does the visible text support the labels?

Sentiment is not severity. An angry comment can concern a minor issue; a calm report can describe a serious safety or availability problem.

## 4. Assign severity conservatively

- **Informational:** no visible problem; general information or curiosity.
- **Low:** limited inconvenience or routine request with no visible material consequence.
- **Medium:** repeated functional, service, delivery, compatibility, or support problem that may affect use.
- **High:** visible inability to use the product, material loss, safety concern, or repeated unresolved failure.
- **Critical:** credible immediate safety, legal, security, or large-scale operational risk.

Every high or critical label requires an evidence-based note and human review before escalation.

## 5. Measure visible response

Link official replies through stable parent IDs or an explicit platform relation. Distinguish useful answers, templates, redirection, and other visible response modes. Report both:

- customer signals with any visible official reply;
- customer signals with a useful visible answer.

Absence of a captured reply means “no visible reply in the declared scope,” not proof that no private or later response occurred.

## 6. Report for action

For every important finding, provide:

1. observation with `n/N`;
2. issue, severity, and confidence;
3. representative evidence IDs and source URLs;
4. cautious interpretation;
5. proposed human review or business experiment.

Keep usernames out of shareable reports. `apply_customer_voice.py` replaces the author field with a stable alias while leaving the raw evidence file unchanged. This is pseudonymization, not complete anonymization: review free text and source URLs for names, phone numbers, addresses, or other personal data before sharing outside the authorized team.
