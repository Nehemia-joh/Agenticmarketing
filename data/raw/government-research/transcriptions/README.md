# Transcriptions of scanned official documents

Some councils publish their lists only as scanned PDFs with no text layer, or as an image on the page. These files transcribe the rows this run uses, with the document's or image's URL, its SHA-256 and the page (or image) and row of every value, so each value can be checked against the original. For a page image, `pdf_page` holds the image's position on the page.

| File | Source | Rows transcribed | Rows left out |
|---|---|---|---|
| `arushadc_madiwani_2025-2030_2026-09-23.csv` | Arusha District Council, "Orodha ya Waheshimiwa Madiwani 2025-2030", attached to its councillors page (2 scanned pages) | The 27 ward councillors: name, ward and phone number as published | Row 1 (the constituency MP, an ex-officio member) and rows 3 and 30–37 (special-seat councillors). They are not ward conveners, so their details were not copied. |
| `arushacc_madiwani_2025-2030_2026-09-26.csv` | Arusha City Council, "Orodha ya Madiwani Arusha Jiji", an image on its councillors page | 25 ward councillors: name and ward | MPs (rows 2 to 4) and special-seat councillors (rows 29 onwards). The gender and party columns were not copied. |
| `merudc_madiwani_2025-2030_2026-09-26.csv` | Meru District Council, "Orodha ya Waheshimiwa Wadiwani 2025-2030", an image on its councillors page | The 25 ward councillors of wards in the catchment: name and ward | The MP, special-seat councillors, Ngabobo ward (outside the catchment) and row 1 (the chair, listed again as King'ori's councillor in row 9) |
| `mondulidc_madiwani_2025-2030_2026-09-26.csv` | Monduli District Council, "Orodha ya Madiwani 2025-2030", an image on its councillors page | The 5 ward councillors of wards in the catchment | The MP, special-seat councillors and wards outside the catchment |
| `moshidc_madiwani_2025-2030_2026-09-26.csv` | Moshi District Council, "Orodha ya Madiwani", the Kiswahili image on its councillors page (the English image lists the same people) | The 4 ward councillors of wards in the catchment | MPs, special-seat councillors, wards outside the catchment, and the gender column |
| `moshimc_madiwani_2025-2030_2026-09-26.csv` | Moshi Municipal Council, "Orodha ya Baraza la Madiwani Manispaa ya Moshi 2025/2030", an image on its councillors page | 16 ward councillors: name, ward and phone as published | The mayor (row 1, whose ward the list does not give, so Njoro ward stays unnamed), special-seat councillors and wards outside the catchment |
| `sihadc_madiwani_2025-2030_2026-09-26.csv` | Siha District Council, "Orodha ya Waheshimiwa Madiwani", the Kiswahili image on its councillors page (the English image lists the same people) | The 9 ward councillors of wards in the catchment | Special-seat councillors and wards outside the catchment |
| `simanjirodc_madiwani_2025-2030_2026-09-26.csv` | Simanjiro District Council, "Orodha ya Madiwani Simanjiro", an image on its councillors page | Naisinyai's councillor, the one ward in the catchment | Every other row |

Rules:
- Copy values exactly as printed, including spelling and capitals. The build step matches ward spellings to the census through `links.json`.
- Write a note for any character that is hard to read, and do not guess silently.
- Each row stays `needs_review` until a person checks it against the scan.
- Copy only the rows the run uses: ward councillors of wards in the catchment. Never copy a party, gender or any other column the run does not use.
- Meru, Moshi District and Moshi Municipal link their images on a `test.` host whose certificate does not match its name. That was not passed: the same file name was fetched from the council's own host, and each row's note says so.
