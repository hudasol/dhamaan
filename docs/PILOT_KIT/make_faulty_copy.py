"""Make a copy of a log with one measurement level GNSS fault, for the walk through (software only, no RF).

Usage: python docs/PILOT_KIT/make_faulty_copy.py IN_GNSS_CSV OUT_GNSS_CSV [KIND SIZE ONSET_S]
Default: a 20 m jump from 30 s, with a fixed seed so the result is the same on every machine.
The copy is SYNTHETIC: it is a stand in log with an injected fault, not a recording.
"""
from __future__ import annotations

import os, sys

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")))
from sim.r2 import replay  # noqa: E402


def main(argv: list[str]) -> int:
    src, dst = argv[0], argv[1]
    kind, size, onset = (argv[2], float(argv[3]), float(argv[4])) if len(argv) >= 5 else ("jump", 20.0, 30.0)
    with open(dst, "w", encoding="utf-8", newline="\n") as f: f.write(replay.faulty_copy(open(src, encoding="utf-8").read(), kind, size, onset))
    print("wrote", dst)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
