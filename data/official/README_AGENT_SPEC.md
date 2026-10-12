Official source check output spec (used by the phase 2 official source subagents).

Write two CSV files with Python's csv module (never hand typed) and confirm they parse:

1. data/official/<name>_items.csv with columns:
   check_id, item, instrument, locator_seen, what_the_source_says, value, source_url, source_type, access_seen, retrieved_on, conflicts, status, table_rows_checked, download_if_blocked
   - locator_seen: the exact article, paragraph, annex, section or page you saw. Never guess one.
   - what_the_source_says: your paraphrase. A quote must be under 15 words and attributed.
   - value: the date, limit or number if the item has one.
   - source_type: official_primary (Official Journal, regulator's own publication), official_service (an official EU or national body page), unofficial, or secondary.
   - access_seen: full text seen (the provision's own wording was returned), summary seen, or not accessible.
   - conflicts: any other source with a different value, with its URL and value; blank if none.
   - status: confirmed (an official source, full text seen, no conflict), conflict, open, or not_accessible.
   - download_if_blocked: the exact URL or document for the user to fetch by hand.
2. data/official/<name>_rows.csv with columns:
   row_id, field, current_value, proposed_value, reason, source_url, locator_seen, access_after
   - One line per proposed change to an evidence table row. field is one of: source_url, access_level, clause_or_section_seen, requirement_paraphrase, edition_or_version, status_note, binding_status, applies_to.
   - Propose only changes your retrieval supports. An official source that returned the provision's own wording lets you propose access_level = full text seen and the official source_url.
