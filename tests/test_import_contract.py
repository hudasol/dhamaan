"""Import contract: lower layers never import higher ones.

Layers, lowest first (see docs/ARCHITECTURE.md):
  0 data      data/, assurance/, schema/      no code
  1 tools     tools/*.py                      validate, check, build, render
  2 sim       sim/*.py                        seeded synthetic simulation
  3 docsgen   docsgen/*.py                    fills documents from data and results
Each layer may import the standard library, its allowed third party packages, and lower layers.
No layer may import an LLM client: no model sits in any decision path.
"""
import ast, os, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
LAYERS = {"tools": 1, "sim": 2, "docsgen": 3}
THIRD_PARTY = {"tools": {"yaml"}, "sim": {"numpy"}, "docsgen": {"yaml"}}
FORBIDDEN = {"openai", "anthropic", "transformers", "langchain", "llama_cpp", "google", "cohere", "mistralai",
             "ollama", "litellm", "requests", "urllib3", "httpx",
             # standard library network modules
             "socket", "ssl", "http", "ftplib", "smtplib", "poplib", "imaplib", "telnetlib", "xmlrpc", "urllib.request"}
STDLIB = set(sys.stdlib_module_names)


def modules(layer):
    """Every module of a layer, subpackages included, as paths relative to the layer without '.py'."""
    d = os.path.join(ROOT, layer)
    out = []
    for dp, dn, fn in os.walk(d):
        dn[:] = [x for x in dn if x != "__pycache__"]
        rel = os.path.relpath(dp, d).replace(os.sep, "/")
        out += [(f[:-3] if rel == "." else f"{rel}/{f[:-3]}") for f in fn if f.endswith(".py")]
    return sorted(out)


OWNER = {m: layer for layer in LAYERS for m in modules(layer) if m != "__init__" and "/" not in m}
OWNER.update({layer: layer for layer in LAYERS})


def imports(path):
    tree = ast.parse(open(path, encoding="utf-8").read(), path)
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                if a.name in FORBIDDEN: yield a.name, n.lineno
                yield a.name.split(".")[0], n.lineno
        elif isinstance(n, ast.ImportFrom):
            if n.level: yield "<relative>", n.lineno
            elif n.module:
                if n.module in FORBIDDEN: yield n.module, n.lineno
                for a in n.names:
                    if f"{n.module}.{a.name}" in FORBIDDEN: yield f"{n.module}.{a.name}", n.lineno
                yield n.module.split(".")[0], n.lineno
        elif isinstance(n, ast.Call) and getattr(n.func, "id", getattr(n.func, "attr", "")) in ("__import__", "import_module"):
            yield "<dynamic>", n.lineno


def violations():
    out = []
    for layer, rank in LAYERS.items():
        for m in modules(layer):
            path = os.path.join(ROOT, layer, m + ".py")
            for name, line in imports(path):
                where = f"{layer}/{m}.py:{line}"
                if name in FORBIDDEN: out.append(f"{where} imports forbidden package {name}")
                elif name == "<dynamic>": out.append(f"{where} uses a dynamic import")
                elif name == "<relative>": continue
                elif name in OWNER:
                    if LAYERS[OWNER[name]] > rank: out.append(f"{where} imports higher layer {OWNER[name]} ({name})")
                elif name not in STDLIB and name not in THIRD_PARTY[layer]:
                    out.append(f"{where} imports {name}, not allowed in layer {layer}")
    return out


def test_import_contract_holds():
    assert violations() == []


def test_contract_detects_upward_import(tmp_path, monkeypatch):
    # A tools module importing a sim module must be reported.
    global ROOT, OWNER
    for layer in LAYERS: (tmp_path / layer).mkdir()
    (tmp_path / "tools" / "a.py").write_text("import b\n", encoding="utf-8")
    (tmp_path / "sim" / "b.py").write_text("import numpy\n", encoding="utf-8")
    (tmp_path / "docsgen" / "c.py").write_text(
        "import openai\nimport urllib.request\nfrom urllib import request\nimport urllib.parse\n", encoding="utf-8")
    old_root, old_owner = ROOT, OWNER
    try:
        ROOT = str(tmp_path)
        OWNER = {m: layer for layer in LAYERS for m in modules(layer)}
        v = violations()
    finally:
        ROOT, OWNER = old_root, old_owner
    assert any("tools/a.py" in x and "higher layer sim" in x for x in v)
    assert any("forbidden package openai" in x for x in v)
    assert sum("forbidden package urllib.request" in x for x in v) == 2
    assert not any("urllib.parse" in x for x in v)
