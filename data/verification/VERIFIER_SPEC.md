# Verifier instructions (passes A, B, C)

You are an independent verifier. You have not seen any earlier verdicts. Do not look in other folders of this repository for earlier results, the notes column or change logs. Use only your input CSV and the fetch/search tools (WebFetch, WebSearch). Do not use curl, wget, mirrors, caches or other workarounds for a site that refuses. Free sources only. Never reproduce paywalled standard text.

For EVERY row of your input CSV:
1. Fetch the row's source_url (WebFetch). If the page is a PDF or long document and the tool returns an extraction, use it; if the tool refuses or times out, retry once, then record `fetch_ok=no`. Read the passage that the row relies on.
2. Decide independently, from what you actually retrieved:
   - `para_verdict`: supported | partly | unsupported | unverifiable. Compare requirement_paraphrase, edition_or_version and status_note with the source. "partly" = some content is right but a number, date, scope, or obligation is wrong or overstated.
   - `locator_seen`: the article, paragraph, clause, section or heading you actually saw that contains the content (blank if none seen). 
   - `clause_ok`: yes | no | na (na if the row has no clause or you saw none).
   - `edition_ok`: yes | no | unverifiable.
   - `binding_value`: your own value from these definitions, NOT copied from the row: mandatory (binding legal text on developer or operator, seen in legal text or official regulator page); conditional (binding only if a trigger holds, or presumption of conformity route); voluntary (standard or practice not required by law in the relevant jurisdiction); guidance (non binding regulator or body guidance).
   - `access_value`: what your retrieval supports: `full text seen` (you read the passage itself), `summary seen` (only a summary, abstract, catalogue blurb or secondary description), `title only` (title and scope only).
   - `recommendation`: keep | revise | downgrade | remove.
   - `corrected_paraphrase`: if revise or downgrade, a short neutral paraphrase of what the source supports (your own words, no quotes over 15 words, no text copied from paywalled standards). For downgrade give title and scope text only.
   - `evidence_note`: one sentence on what you saw (include a short attributed quote only if essential, under 15 words).
3. Do not assume a row is right because it looks plausible. Do not invent clause numbers. If a source is unreachable, say so and set para_verdict=unverifiable, access_value=title only unless the URL gives at least a title and scope you could read.
4. Be efficient: group rows with the same URL under one fetch.

OUTPUT: write a CSV with a Python csv module (never by hand string concatenation) to the path given in your task, with exactly these columns:
id,fetch_ok,para_verdict,locator_seen,clause_ok,edition_ok,binding_value,access_value,recommendation,corrected_paraphrase,evidence_note
One row per input row, same ids. Verify afterwards that the file parses and has all ids. Your final message: only the output path, count of rows, and counts of each para_verdict. 
