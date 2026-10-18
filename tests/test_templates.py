"""The case templates must pass the checker with flags and zero errors, keep every item open, and start a case."""
import glob, os, sys
import yaml
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import ac_check as ac
from dhamaan import cli

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATES = sorted(glob.glob(os.path.join(ROOT, "assurance", "templates", "*.yaml")))
ROWS = ac.table_rows(os.path.join(ROOT, "data", "evidence_table.csv"))


def test_three_templates_exist():
    assert {os.path.basename(p)[:-5] for p in TEMPLATES} == {"indoor_delivery_robot", "survey_drone", "outdoor_rover"}


def test_each_template_has_flags_and_zero_errors():
    for p in TEMPLATES:
        res = ac.check(ac.load(p), ROWS, ROOT)
        assert [r for r in res if r[0] == "ERROR"] == [], p
        assert any(r[0] == "FLAG" for r in res), p


def test_templates_keep_every_item_open_and_cite_real_rows():
    for p in TEMPLATES:
        case = yaml.safe_load(open(p, encoding="utf-8"))
        assert all(e["status"] == "open" for e in case["evidence"]), p
        assert all(r in ROWS for e in case["evidence"] for r in e["rows"]), p
        assert "TEMPLATE (proposal)" in open(p, encoding="utf-8").read().splitlines()[0], p


def test_new_case_starts_from_each_real_template(tmp_path, capsys):
    for p in TEMPLATES:
        name = os.path.basename(p)[:-5]
        assert cli.main(["new-case", name, "--out", str(tmp_path / f"{name}.yaml")]) == 0
        assert "0 errors" in capsys.readouterr().out
