---
name: screenshot-to-table-ingestion
description: Convert screenshots, OCR text, pasted app text, or partially structured visual data into validated editable table records. Use when the user wants to extract data from phone screenshots or app pages, match missing identifiers, preview records, correct recognition errors, and write normalized rows into a spreadsheet, Bitable, database, or app state.
---

# Screenshot To Table Ingestion

## Purpose

Turn unreliable visual or pasted input into reliable structured records. The core product is not OCR; it is a validated, editable ingestion loop.

## Non-Negotiables

- Never treat screenshot recognition as final data.
- Always show extracted rows in an editable table or explicit preview before writing.
- If identity matching is uncertain, stop and ask for confirmation.
- Preserve the user's ability to paste text or manually enter rows when image recognition is unavailable.
- Write normalized field names and values, not raw OCR layout fragments.

## Workflow

1. Define the target schema.
   - Required fields
   - Optional fields
   - Field types: text, number, date, percent, enum, currency
   - Primary identifiers and matching keys

2. Extract data.
   - Prefer structured vision or OCR output with a strict JSON shape.
   - For pasted text, parse by rows and visible labels.
   - Keep raw extraction available for debugging when useful.

3. Normalize values.
   - Strip commas, currency symbols, whitespace, and percent signs.
   - Store percentages consistently as numeric percent or decimal according to the destination schema.
   - Convert dates to a stable format such as ISO date.
   - Deduplicate by primary key plus date when applicable.

4. Match missing identifiers.
   - Prefer exact visible code or id.
   - Then use alias tables, normalized names, and fuzzy matching.
   - Track confidence. If confidence is low, do not write.

5. Validate.
   - Required fields present
   - Numeric fields parse correctly
   - Record count matches expected count when known
   - Totals reconcile when account values are present
   - Same-date duplicate behavior is explicit

6. Preview and edit.
   - Show extracted rows in the same columns that will be written.
   - Make missing or suspicious fields visible.
   - Let the user correct values before the write action.

7. Write and verify.
   - Write only after preview/edit.
   - Report counts written.
   - Read back or otherwise verify when tooling supports it.

## App UI Pattern

Use this sequence on the working screen:

```text
Upload or paste input
Recognize
Editable table
Validation messages
Preview destination records
Write
Written-count confirmation
```

## Failure Handling

- If OCR fails, keep the editable table available for manual entry.
- If a field cannot be matched confidently, show the unmatched value and the candidate matches.
- If write fails, output the exact records that would have been written and the missing permission/tool/config.

