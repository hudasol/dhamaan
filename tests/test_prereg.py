"""The preregistration, predictions and acceptance values are frozen once committed."""
import hashlib, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from sim.predictions import ACCEPTANCE, PREDICTIONS

ROOT = os.path.join(os.path.dirname(__file__), "..")
FROZEN = ("sim/PREREGISTRATION.md", "sim/predictions.py", "sim/acceptance.py")


def recorded():
    out = {}
    for line in open(os.path.join(ROOT, "sim/PREREGISTRATION.sha256.txt"), encoding="utf-8"):
        if line.strip() and not line.startswith("#"):
            h, p = line.split(None, 1); out[p.strip()] = h
    return out


def test_preregistration_files_unchanged():
    rec = recorded()
    for p in FROZEN:
        assert hashlib.sha256(open(os.path.join(ROOT, p), "rb").read()).hexdigest() == rec[p], p


def test_document_lists_every_prediction_verbatim():
    md = open(os.path.join(ROOT, "sim/PREREGISTRATION.md"), encoding="utf-8").read()
    for p in PREDICTIONS:
        assert f"| {p['id']} | {p['text']} |" in md, p["id"]
    for a in ACCEPTANCE:
        assert f"| {a['id']} |" in md, a["id"]
