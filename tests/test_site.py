"""The static site: self contained, banner on every page, built from data, accessible basics, Arabic page marked."""
import csv, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from docsgen import facts as F, site
from docsgen.markdown import to_html

ROOT = site.ROOT
PAGES = site.build_site()


def test_every_nav_page_is_built():
    assert set(PAGES) == {h for h, _ in site.NAV}


def test_deterministic():
    assert site.build_site() == PAGES


def test_banner_on_every_page():
    for name, text in PAGES.items():
        assert 'class="banner" role="note"' in text, name
        assert ("not endorsed by any entity" in text) or ("ولا تحظى بتأييد أي جهة" in text), name


def test_self_contained_no_external_resources():
    for name, text in PAGES.items():
        assert not re.search(r"<script[^>]+src=", text), name
        assert not re.search(r"<link[^>]+(stylesheet|preload|icon)", text), name
        assert not re.search(r"<(img|iframe|source|video|audio)[^>]+src=[\"']https?:", text), name
        assert "@import" not in text and "url(http" not in text and "fonts.googleapis" not in text, name


def test_evidence_page_lists_every_row_of_the_table():
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data/evidence_table.csv"), encoding="utf-8", newline="")))
    text = PAGES["evidence.html"]
    assert text.count("<tr data-family=") == len(rows)
    for r in rows: assert f"<td>{r['id']}</td>" in text


def test_case_page_svg_covers_every_case_node():
    dot = open(os.path.join(ROOT, "figures/gsn_library_robot.dot"), encoding="utf-8").read()
    svg = open(os.path.join(ROOT, "figures/gsn_library_robot.svg"), encoding="utf-8").read()
    nodes = set(re.findall(r"^\s+((?:G|SN_EV)\w+) \[", dot, re.M))
    titles = set(re.findall(r"<title>([^<]+)</title>", svg))
    assert nodes and nodes <= titles, "re-render figures from CI: the SVG is older than the DOT source"


def test_index_numbers_come_from_facts():
    f = F.all_facts(); text = PAGES["index.html"]
    for k in ("N_ROWS", "N_OPEN", "N_EVIDENCE_ITEMS", "PRED_HIT", "R2_PRED_HIT"): assert f[k] in text


def test_arabic_page_is_rtl_and_marked_as_a_draft():
    t = PAGES["ar.html"]
    assert '<html lang="ar" dir="rtl">' in t and "draft for owner review" in t


def test_pages_have_language_title_and_landmarks():
    for name, t in PAGES.items():
        assert re.search(r'<html lang="(en|ar)"', t) and "<title>" in t and "<main>" in t and 'aria-label="Pages"' in t, name


def test_markdown_basics():
    h = to_html("# T\n\nA **b** `c` [d](e.md)\n\n| x | y |\n|---|---|\n| 1 | 2 |\n\n- i\n- j\n")
    assert "<h1>T</h1>" in h and "<strong>b</strong>" in h and "<code>c</code>" in h and '<a href="e.md">d</a>' in h
    assert "<td>1</td>" in h and "<li>i</li>" in h


def test_site_voice_rules():
    banned = re.compile("—|" + r"\bClaude\b|\bAnthropic\b|ChatGPT|subagent|WebFetch|WebSearch|fetch tool|permission layer|universit", re.I)
    for name, t in PAGES.items():
        visible = re.sub(r"<script>.*?</script>", "", t, flags=re.S)
        if name in ("evidence.html", "coverage.html"):   # rows of the frozen table name cited publishers (review finding R20)
            visible = re.sub(r"<tbody>.*?</tbody>", "", visible, flags=re.S)
        assert not banned.search(visible), (name, banned.search(visible).group(0))
