"""Proposal pack: generated from data, no institution names, no implied endorsement, every label stated."""
import glob, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from docsgen import build as B

ROOT = B.ROOT
BRIEFS = {rel: text for rel, text in B.build().items() if rel.startswith("docs/PROPOSAL/")}
NAMES = re.compile(r"\b(GCAA|RTA|EASA|FAA|ICAO|MOIAT|EDGE|TII|ATRC|ADEO|NASA|BSI|IEEE)\b|University|Institute of|Council|Ministry|Authority\b")


def test_three_briefs_and_a_limits_note():
    names = {os.path.basename(r) for r in BRIEFS}
    assert names == {"BRIEF_RESEARCH_INSTITUTE.md", "BRIEF_INDUSTRIAL_INTEGRATOR.md", "BRIEF_GOVERNMENT_OFFICE.md", "LIMITS_NOTE.md"}


def test_no_institution_names():
    for rel, t in BRIEFS.items():
        m = NAMES.search(t); assert m is None, (rel, m and m.group(0))


def test_endorsement_is_only_ever_denied():
    for rel, t in BRIEFS.items():
        for m in re.finditer(r"endors\w*", t, re.I):
            assert re.search(r"\b(not|no)\b", t[max(0, m.start() - 80):m.start()], re.I), (rel, t[max(0, m.start() - 80):m.end()])


def test_briefs_state_every_label_and_what_is_not_claimed():
    for rel, t in BRIEFS.items():
        if rel.endswith("LIMITS_NOTE.md"): continue
        for w in ("Documented", "Interpreted", "Simulated", "Open", "## What is not claimed", "## The ask", "SYNTHETIC"):
            assert w in t, (rel, w)
