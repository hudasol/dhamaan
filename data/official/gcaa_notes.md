# GCAA official source check, 2026-10-12

## Outcome in one line
The primary documents (CAR-UAC, CAR-UAEX, CAAP 22) could NOT be retrieved. The fetch tool rejected every long GCAA PDF URL (HTTP 403, "url exceeds the maximum fetchable length") and the GCAA listing page request timed out on permission (PROVENANCE_REQUIRED). Nothing was worked around. The section by section value comparison requested (VLOS, daylight, 400 ft, 25 kg, goods, SORA version, 3 hour deadline, UOA, MOIAT letter, 24 months, insurance, pilot licence) is therefore NOT done; those items are `not_accessible`.

## What was seen
- Search index titles (not the listing page): CAR-UAC Issue 02; CAR-UAEX Issue 02 and Issue 02 (Corrected); CAR-UAR Issues 02, 03, 04; CAR-UAD Issue 02 / 02 (Corrected); CAR-UAEV Issue 02; CAR UA-ATO Issue 01; CAR-UAM Issue 1. No later CAR-UAC or CAR-UAEX issue appeared, but this is not proof of absence. No dates were seen.
- CAR-UAS Issue 01 header (fetch extraction, a summary): issued 6 Feb 2018, applicable 4 Mar 2018, no supersession statement. C58 supersession stays unconfirmed.
- GCAA Reporting page (extraction): cites CAR-OCR Issue 01, Jan 2025; drones or unlawful interference listed among events to report immediately. Matches D46 at page level only.
- u.ae English aviation safety page (extraction): last updated 02 Sep 2026 (C62 has 19 Nov 2025 from the Arabic page); UOA with AED 1,200 fee; Security Clearance; accidents reported immediately to GCAA hotline. No 3 hour figure in the extraction.
- U-space: trade article (secondary) dated 14 Mar 2025, "CAR Airspace Part Uspace", no issue or effective date; linked proposal NPA 2024-05 Issue 01.

## New finding that may matter
GCAA Safety Decision 2026-03 (temporary suspension of drones and other recreational and specialised aircraft). Gulf News (updated 1 Mar 2026) reports a one week suspension of all drone flight permits with immediate effect, to be reviewed. GCAA search titles show Issues 01, 02 and 03 of this decision. I did not read the decisions, so I do not know whether it is lifted or still in force. The table has no row for it. Recommend a manual read before the study states that the CAR-UAC default limits apply.

## Items for manual download (exact URLs in gcaa_items.csv)
CAR-UAC Issue 02, CAR-UAEX Issue 02 (Corrected), CAR-UAR Issue 04, CAAP 22 Issue 05, Safety Decision 2026-03 Issue 03, CAR-OCR, and the GCAA CARs listing to read issue numbers and dates.

## Tool limits
All fetches returned model extractions, not the documents' own wording. No quotes are given. No row is upgraded; no `full text seen` claim is made here. Rows C51 to C56 and D45 keep their earlier access level, which this run neither confirms nor contradicts.
