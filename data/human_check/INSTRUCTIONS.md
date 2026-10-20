# How to do the human check

Time: about 5 minutes a row, 10 at most. Wave 1 is positions 1 to 30. Do wave 1 first; wave 2 is optional but halves the interval.

Rules for the reader:
1. Read the source yourself. Do not use an assistant tool to read it or to decide a column.
2. Open `data/human_check/worksheet.csv` in a spreadsheet program. Work in order of `position`.
3. For each row open `source_url`. Find the passage that the `requirement_paraphrase` is about. If the row gives a locator in `clause_or_section_seen`, go to it.
4. Fill the four response columns:
   - `paraphrase_supported`: `yes` if the source says what the paraphrase says; `partly` if something is right but a number, date, scope or obligation is wrong or overstated; `no` if the source does not say it; `cannot_open_source` if the page is blocked, missing or paywalled.
   - `binding_assigned`: your own reading, from the definitions below. `cannot_tell` if the source does not let you decide.
   - `access_achieved`: `full text` (you read the passage itself), `summary` (only an abstract, catalogue entry or secondary description), `title only`, or `could_not_open`.
   - `locator_found`: `yes`, `no`, or `not_applicable` if the row gives no locator.
5. Put minutes spent in `minutes` and anything odd in `notes` (one line).
6. Do not change any other column. Do not look up the table's own binding status or access level before you answer.
7. Save the finished file as `worksheet_completed.csv` in the same folder (UTF-8 CSV). Then run:
   `python tools/human_check.py score`

Binding definitions (from `docs/PROTOCOL.md`):
- mandatory: binding legal text on the developer or operator, seen in legal text or an official regulator page.
- conditional: binding only if a trigger holds (risk class, category, harmonised standard route, approval pathway).
- voluntary: not referenced by law in the relevant jurisdiction.
- guidance: regulator or body guidance that is not binding.

Fourteen of the 60 rows point to EUR-Lex. Reading the Machinery Regulation and the AI Act pages for these rows also settles most items in `docs/FETCH_LIST.md`, so do both in one sitting.
