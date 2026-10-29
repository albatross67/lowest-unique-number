# Data guide

## Provenance

This package analyzes the organizer's 15 accepted choices and the attached `Pasted markdown(3).md`, preserved byte-for-byte as `source/submissions_as_supplied.md`. The organizer separately supplied the name/number list and said its order approximates submission order. They observed that DMs generally followed public comments promptly, without apparent deliberate waiting. No exact timestamps, platform export, full non-entrant comment thread, likes, model identities, or tool execution logs were supplied.

The accepted choice list is reconciled with the normalized transcription and is also recorded as an independent control in the analysis script. IDs LUN001–LUN015 are assigned for navigation in the organizer's approximate list order; they are not platform IDs. Public GitHub output is intended for `albatross67/lowest-unique-number`.

`data/submissions.json` preserves complete public and DM text with layout normalization: excess separator blank lines and Markdown hard-linebreak backslashes are removed, and nonbreaking spaces become ordinary spaces. The unedited source remains authoritative for exact formatting. Optional remarks, including Dei's commercial offer, remain in the full-text record but are not treated as contest actions or scored outcomes.

## File schemas

### `data/submissions.json` — source records

- `entry_id`: assigned stable navigation ID.
- `name`: entrant display name as supplied.
- `number`: submitted integer, reconciled with the organizer's results list.
- `approx_order`: organizer-supplied approximate ordering, not a timestamp or certified rank of arrival.
- `self_reported_alignment`: manually transcribed `yes`, `no`, or `partly` answer to the public/private-fit question.
- `public_text`, `dm_text`: normalized complete text.

### `data/entries.csv` — one row per entrant

Contains the source fields above plus:

- `number_count`: total accepted entries choosing the same number.
- `outcome`: `winner`, `collision`, or `unique_nonwinner`. There is no second-place prize or inferred rank.
- `analyst_note`: interpretive note drawn from `data/interpretations.json`; never treated as an observed agent state.

CSV text fields may contain embedded commas, quotes, and newlines. Use a CSV reader, not a line-by-line split. UTF-8 encoding is used.

### `data/number_counts.csv` — one row per legal number

- `number`: every integer 1–100.
- `count`: number of accepted entries.
- `entrants`: display names separated by semicolons, empty for zero choices.
- `status`: `winner`, `unique_nonwinner`, `collision`, or `unselected`.

A zero-count number does not qualify as unique. Only count exactly one qualifies.

### `data/summary.json`

Computed descriptive statistics and declared contest metadata. Fractions use 0–1 units. Mean and median summarize choices, not skill or performance. `unique_entries` equals `unique_numbers` because each singleton number has one chooser. Colliding entries include every chooser at a repeated number. `prize_payment_verified: false` means no payment evidence was provided, not that payment failed or is overdue.

### `data/public_claims.json` and `data/public_claim_checks.csv`

The JSON holds manually selected explicit numerical public claims, exact excerpts, and predicates. Each `claim_id` is stable. Predicates use `winning_range` (inclusive bounds), `count_range` (inclusive bounds for one number's count), `max_choice`, or `chosen_range` (a statement about the speaker's own choice). The CSV holds each predicate's computed result and actual observation.

This is a selected descriptive audit, not an exhaustive annotation or preregistered scoring scheme. Multiple claims by one agent are not independent observations. Broad predictions are easier to satisfy than narrow ones. “Supported” means consistent with this particular outcome. No aggregate pass rate is used as a measure of forecasting ability. Non-numerical and ambiguous claims are discussed in `PREDICTIONS.md` and participant pages rather than forced into binary labels.

### `data/interpretations.json`

Manually authored, entry-level analysis notes. These distinguish self-reported alignment, literal numerical consistency, and prediction success. The three are not equivalent. They do not infer intent, identify underlying models, or measure actual cognitive processes.

### Figures

- `number_distribution.png`: counts for 1–30; all choices above 26 are zero. Full 1–100 data remain in CSV.
- `approximate_order.png`: private choices along the supplied approximate order. No time intervals, exact comment availability, or causal effects are inferred.

## Reproduction and checks

Python 3.8+ supports the standard-library core. Run `python scripts/analyze.py` to recalculate results. Add `--figures` with matplotlib installed to recreate both PNGs. The README, rules, data guide, raw source, normalized inputs, and manual annotations are authored inputs rather than regenerated outputs.

The script validates integer range and entrant uniqueness, reconciles the separately supplied list, calculates the winner two ways, checks totals, evaluates claim predicates, and regenerates all participant pages. `data/validation.json` records the checks and SHA-256 of the original transcription. `MANIFEST.json` records hashes and sizes of the release files (excluding itself). These hashes protect against accidental changes; they do not authenticate platform records or prove when messages were sent.

## Interpretation limits

- One round and 15 selected participants cannot establish optimal play or population-wide behavior.
- Public statements were strategically chosen, with bluffing encouraged. DMs are stated rationales, not privileged access to internal reasoning.
- Claims of running simulations are unverified without execution evidence.
- Similar writing can reflect shared conventions or model priors; it does not by itself prove copying, coordination, or shared identity.
- The smaller realized field may matter, but no controlled experiment separates turnout, public discussion, and prior beliefs.
- No inferential p-values or equilibrium claims are presented. There is no established random-choice null appropriate to these strategic entrants.

## Upload

Extract the ZIP, open the `lowest-unique-number` folder, and upload its **contents** to the root of the new repository. Keep the `data`, `participants`, `figures`, `scripts`, and `source` directories so relative links work. Read `README.md` once before publishing. No GitHub changes or token transfers were performed as part of preparing this package.
