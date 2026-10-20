"""The three command reproduction: each command exists, and the document regeneration leg is current."""
import importlib.util, os, re, subprocess, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def _commands():
    text = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    block = re.search(r"## Run it\s+```\n(.*?)```", text, re.S).group(1)
    return [l.strip() for l in block.splitlines() if l.strip()]


def test_readme_gives_three_commands_that_exist():
    cmds = _commands()
    assert len(cmds) == 3, cmds
    assert cmds[0].startswith("python -m pip install")
    assert os.path.exists(os.path.join(ROOT, "pyproject.toml"))
    assert cmds[1] == "python -m sim.run_all" and importlib.util.find_spec("sim.run_all")
    assert cmds[2] == "python tools/fast_check.py" and os.path.exists(os.path.join(ROOT, "tools", "fast_check.py"))


def test_regenerating_documents_changes_nothing():
    r = subprocess.run([sys.executable, "-m", "docsgen.build", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert r.returncode == 0, r.stdout[-500:]


def test_every_doc_is_listed_in_the_reading_order():
    idx = open(os.path.join(ROOT, "docs", "README.md"), encoding="utf-8").read()
    missing = [f for f in sorted(os.listdir(os.path.join(ROOT, "docs"))) if f.endswith(".md") and f != "README.md" and f not in idx]
    assert missing == [], missing
