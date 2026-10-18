"""The round 2 preregistration, predictions and acceptance values are frozen once committed."""
import hashlib, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sim.r2.predictions_r2 import ACCEPTANCE, PREDICTIONS

ROOT = os.path.join(os.path.dirname(__file__), "..")
FROZEN = ("sim/PREREGISTRATION_R2.md", "sim/r2/predictions_r2.py", "sim/r2/acceptance_r2.py")


def recorded():
    out = {}
    for line in open(os.path.join(ROOT, "sim/PREREGISTRATION_R2.sha256.txt"), encoding="utf-8"):
        if line.strip() and not line.startswith("#"):
            h, p = line.split(None, 1); out[p.strip()] = h
    return out


def test_round2_preregistration_files_unchanged():
    rec = recorded()
    for p in FROZEN:
        assert hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest() == rec[p], p


def test_round2_document_lists_every_prediction_and_criterion_verbatim():
    md = open(os.path.join(ROOT, "sim/PREREGISTRATION_R2.md"), encoding="utf-8").read()
    for p in PREDICTIONS: assert f"| {p['id']} | {p['text']} |" in md, p["id"]
    for a in ACCEPTANCE: assert f"| {a['id']} | {a['text']} | {'hold' if a['expect'] else 'fail'} |" in md, a["id"]
