# Transcriptions of scanned official documents

Some councils publish their lists only as scanned PDFs with no text layer. These files transcribe the rows this run uses, with the document's URL, its SHA-256 and the page and row of every value, so each value can be checked against the original.

| File | Source | Rows transcribed | Rows left out |
|---|---|---|---|
| `arushadc_madiwani_2025-2030_2026-09-23.csv` | Arusha District Council, "Orodha ya Waheshimiwa Madiwani 2025-2030", attached to its councillors page (2 scanned pages) | The 27 ward councillors: name, ward and phone number as published | Row 1 (the constituency MP, an ex-officio member) and rows 3 and 30–37 (special-seat councillors). They are not ward conveners, so their details were not copied. |

Rules:
- Copy values exactly as printed, including spelling and capitals. The build step matches ward spellings to the census through `links.json`.
- Write a note for any character that is hard to read, and do not guess silently.
- Each row stays `needs_review` until a person checks it against the scan.
