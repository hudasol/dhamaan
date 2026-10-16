#!/usr/bin/env python3
"""Small regex secrets scan (standard library). CI also runs detect-secrets. Exit 1 on any hit."""
from __future__ import annotations
import os, re, sys
PATTERNS = {
 "private key block": r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----",
 "AWS access key id": r"\bAKIA[0-9A-Z]{16}\b",
 "GitHub token": r"\b(ghp|gho|ghu|ghs|ghr|github_pat)_[A-Za-z0-9_]{20,}\b",
 "Slack token": r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b",
 "Google API key": r"\bAIza[0-9A-Za-z_\-]{35}\b",
 "generic secret assignment": r"(?i)\b(api[_-]?key|secret|passwd|password|token)\b\s*[:=]\s*['\"][A-Za-z0-9/+_\-]{16,}['\"]",
 "JWT": r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
 "credential in URL": r"https?://[^/\s:@]+:[^/\s:@]+@",
 "email address (check it is meant to be public)": r"\b[A-Za-z0-9._%+-]+@(gmail|outlook|hotmail|yahoo)\.[a-z]{2,}\b",
}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}
def scan(root: str) -> list[tuple[str, str, int]]:
    """Return (path, pattern name, line) for each hit under root."""
    hits = []
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            p = os.path.join(dp, f); rel = os.path.relpath(p, root)
            if rel in ("tools/secrets_scan.py",) or rel.startswith("tests/"): continue
            try: t = open(p, encoding="utf-8").read()
            except Exception: continue
            for name, pat in PATTERNS.items():
                for m in re.finditer(pat, t):
                    hits.append((rel, name, t.count("\n", 0, m.start()) + 1))
    return hits
if __name__ == "__main__":
    h = scan(sys.argv[1] if len(sys.argv) > 1 else ".")
    for r, n, l in h: print(f"HIT {r}:{l} {n}")
    print(f"{len(h)} hits"); sys.exit(1 if h else 0)
