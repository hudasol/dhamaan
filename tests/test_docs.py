"""Documents must agree with the data: generated documents are current, templates carry no hand typed
numbers, synthetic numbers carry the label, and public text follows the voice rules."""
import glob, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from docsgen import build as B
from docsgen import facts as F

ROOT = B.ROOT
BUILT = B.build()

# Digits in templates are allowed only inside these (everything else must be a {{FACT}}).
ALLOWED = [
    r"\{\{[A-Z0-9_]+\}\}",                     # placeholders
    r"`[^`\n]*`",                              # code spans
    r"```.*?```",                              # code blocks
    r"\]\([^)]*\)",                            # link targets
    r"https?://\S+",                           # URLs
    r"\b\d{4}-\d{2}-\d{2}\b",                  # ISO dates
    r"\b[A-Za-z][A-Za-z]*[-_]?\d+[A-Za-z0-9.]*\b",  # identifiers: G4, EV-08, DU3, AC-N1, ADR-0001, v0.6.0
    r"\bsection \d+(\.\d+)*",                  # section references
    r"\b(ISO|IEC|EN|UL|PAS|Regulation \(EU\)|Directive|Decree-Law|Resolution|Law)\s?[\d/.:-]+[\d]",  # instrument names
    r"\bCC BY 4\.0\b", r"\b95 percent interval", r"^\s*\d+\.\s",  # licence name, interval level, list markers
]
ALLOWED_RE = re.compile("|".join(f"(?:{a})" for a in ALLOWED), re.M | re.S)


def test_generated_documents_are_current():
    assert B.stale(BUILT) == [], "run: python -m docsgen.build"


def test_templates_have_no_hand_typed_numbers():
    bad = []
    for p in sorted(glob.glob(os.path.join(ROOT, "docs", "templates", "*.tmpl.md"))):
        text = ALLOWED_RE.sub(" ", open(p, encoding="utf-8").read())
        for m in re.finditer(r"\d+", text):
            line = text[:m.start()].count("\n") + 1
            bad.append(f"{os.path.basename(p)}:{line}: {text[max(0, m.start() - 30):m.end() + 30]!r}")
    assert bad == [], bad[:10]


def test_every_template_is_built():
    tmpls = {os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "docs", "templates", "*.tmpl.md"))}
    assert tmpls <= set(B.OUTPUTS.values())


def test_synthetic_numbers_carry_the_label():
    facts = F.all_facts()
    sim_keys = set(F.sim_facts())
    for rel, text in BUILT.items():
        tmpl = open(B.template_path(B.OUTPUTS[rel]), encoding="utf-8").read()
        if set(B.PLACEHOLDER.findall(tmpl)) & sim_keys:
            assert "SYNTHETIC" in text, rel


PUBLIC = ["README.md", "HANDOFF.md"] + [p for p in glob.glob(os.path.join(ROOT, "docs", "*.md"))] \
    + glob.glob(os.path.join(ROOT, "docs", "adr", "*.md")) + ["sim/PREREGISTRATION.md", "sim/DEVIATIONS.md"]


def public_texts():
    for p in PUBLIC:
        p = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if os.path.exists(p): yield os.path.relpath(p, ROOT), open(p, encoding="utf-8").read()


def test_voice_rules_in_public_documents():
    banned = re.compile(r"—|\bClaude\b|\bAnthropic\b|ChatGPT|Co-Authored-By|claude\.ai", re.I)
    emoji = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
    allowed_emoji = {"\U0001F337", "\U0001F338", "\U0001F34B", "\U0001F33F"}
    bad = []
    for rel, t in public_texts():
        for m in banned.finditer(t): bad.append(f"{rel}: {m.group(0)!r}")
        for m in emoji.finditer(t):
            if m.group(0) not in allowed_emoji: bad.append(f"{rel}: emoji {m.group(0)!r}")
    assert bad == [], bad[:10]


def test_hand_written_row_counts_agree_with_table():
    n = F.evidence_table_facts()["N_ROWS"]
    bad = []
    for rel, t in public_texts():
        for m in re.finditer(r"\b(\d+)[ -]row (?:table|evidence table)\b|\ball (\d+) rows\b(?! that)", t):
            got = m.group(1) or m.group(2)
            if got != n: bad.append(f"{rel}: {m.group(0)!r} but the table has {n} rows")
    assert bad == []
