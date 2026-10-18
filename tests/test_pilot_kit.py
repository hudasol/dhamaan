"""Pilot kit: schemas current and consistent with the replay harness, walk through reproducible, hand written pages free of hand typed numbers."""
import glob, json, os, re, subprocess, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import gen_log_schema as gl
from docsgen import facts as F
from sim.r2 import replay
from test_docs import ALLOWED_RE

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
KIT = os.path.join(ROOT, "docs", "PILOT_KIT")


def test_log_schemas_are_current():
    assert gl.stale() == [], "run: python tools/gen_log_schema.py"


def test_schemas_match_the_replay_harness_columns():
    g = json.load(open(os.path.join(KIT, "schemas", "gnss.schema.json"), encoding="utf-8"))
    o = json.load(open(os.path.join(KIT, "schemas", "odometry.schema.json"), encoding="utf-8"))
    assert tuple(g["required"]) == replay.GNSS_COLUMNS and tuple(g["x-column-order"]) == replay.GNSS_COLUMNS + replay.REF_COLUMNS
    assert tuple(o["required"]) == replay.ODO_COLUMNS
    for s in glob.glob(os.path.join(KIT, "schemas", "*.json")):
        assert json.load(open(s, encoding="utf-8"))["x-rate-provenance"] == "assumed, proposal"


def test_walkthrough_script_reproduces_the_documented_result(tmp_path):
    out = tmp_path / "gnss_jump.csv"
    subprocess.run([sys.executable, os.path.join(KIT, "make_faulty_copy.py"), os.path.join(ROOT, "sim/results_r2/standin_log/gnss.csv"), str(out)],
                   check=True, capture_output=True, cwd=str(tmp_path))
    o = replay.read_csv(open(os.path.join(ROOT, "sim/results_r2/standin_log/odometry.csv"), encoding="utf-8").read(), replay.ODO_COLUMNS)
    res = replay.score_log(replay.read_csv(out.read_text(encoding="utf-8"), replay.GNSS_COLUMNS), o)
    assert f'fault declared at t = {res["t_alarm"]:.1f} s ({res["reason"]})' == F.kit_facts()["KIT_FAULT_RESULT"]


def test_hand_written_kit_pages_have_no_hand_typed_numbers():
    generated = {"LOGGING_SPEC.md", "WALKTHROUGH.md"}
    bad = []
    for p in glob.glob(os.path.join(KIT, "*.md")):
        if os.path.basename(p) in generated: continue
        text = ALLOWED_RE.sub(" ", open(p, encoding="utf-8").read())
        bad += [f"{os.path.basename(p)}: {text[max(0, m.start() - 25):m.end() + 25]!r}" for m in re.finditer(r"\d+", text)]
    assert bad == []
