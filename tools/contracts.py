"""Typed contracts for the two data files every other layer depends on.

Layer: tools (lowest code layer). Standard library only. This module imports nothing from the repository.

- EVIDENCE_TABLE: the columns of data/evidence_table.csv, with allowed values and formats.
- CASE: the node kinds and fields of assurance/library_robot_case.yaml.

The JSON schemas in schema/ are generated from these definitions (tools/gen_schema.py) and a test fails
when the committed schema files are stale. The value sets below are the single source used by
tools/validate_table.py and tools/ac_check.py.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

__all__ = ["Column", "Field", "NodeKind", "EVIDENCE_TABLE", "CASE", "CASE_TOP_LEVEL",
           "BINDING", "ACCESS", "BINDING_CHECKED", "VERIFICATION_STATUS", "EVIDENCE_STATUS",
           "case_conformance"]

# ---- evidence table -------------------------------------------------------------------------

BINDING: tuple[str, ...] = ("mandatory", "conditional", "voluntary", "guidance")
ACCESS: tuple[str, ...] = ("full text seen", "summary seen", "title only")
BINDING_CHECKED: tuple[str, ...] = ("agreed", "agreed (3 of 3)", "majority of 3", "split", "disputed")
VERIFICATION_STATUS: tuple[str, ...] = (
    "verified twice, no change", "verified three times", "confirmed by final check",
    "corrected after final check, single checked", "corrected after A/B, not re-checked",
    "flagged by final check, no replacement text", "source not fully retrieved by verifier")


@dataclass(frozen=True)
class Column:
    """One column of the evidence table."""
    name: str
    description: str
    non_empty: bool = False
    enum: tuple[str, ...] = ()
    pattern: str = ""


ISO_DATE = r"^\d{4}-\d{2}-\d{2}$"

EVIDENCE_TABLE: tuple[Column, ...] = (
    Column("id", "Row id: stream letter A to D and two digits.", True, pattern=r"^[A-D]\d{2}$"),
    Column("family", "Instrument family (own grouping).", True),
    Column("instrument", "Instrument name as seen in the source.", True),
    Column("edition_or_version", "Edition or version as seen."),
    Column("status_note", "Status of the instrument as seen, with dates."),
    Column("clause_or_section_seen", "Locator a verifier saw in full text; empty unless access is full text seen."),
    Column("requirement_paraphrase", "Short paraphrase of what the source asks. Never source text.", True),
    Column("binding_status", "How binding the item is for a developer.", True, enum=BINDING),
    Column("applies_to", "System types the row applies to."),
    Column("evidence_type", "Kind of evidence asked for, in words."),
    Column("evidence_codes", "Evidence type codes E00 to E15, separated by '; '.", True),
    Column("who_verifies", "Who checks the evidence, as seen."),
    Column("source_url", "Single http(s) URL of the source retrieved.", True, pattern=r"^https?://[^\s;]+$"),
    Column("retrieval_date", "Date the source was retrieved.", True, pattern=ISO_DATE),
    Column("access_level", "What the reader actually saw.", True, enum=ACCESS),
    Column("notes", "Free notes."),
    Column("clause_reported_unverified", "Locator reported but not seen in full text by a verifier."),
    Column("binding_checked", "Agreement of verifiers on binding status.", True, enum=BINDING_CHECKED),
    Column("verification_status", "Outcome of the phase 2 verification for this row.", True, enum=VERIFICATION_STATUS),
    Column("last_checked", "Date the row was last checked.", True, pattern=ISO_DATE),
)

# ---- assurance case -------------------------------------------------------------------------

EVIDENCE_STATUS: tuple[str, ...] = ("open", "partial", "provided")


@dataclass(frozen=True)
class Field:
    """One field of a node in the assurance case. kind is one of: string, boolean, ids."""
    name: str
    kind: str
    description: str
    required: bool = False
    enum: tuple[str, ...] = ()
    pattern: str = ""


@dataclass(frozen=True)
class NodeKind:
    """A list of nodes under one top level key of the case file."""
    key: str
    id_pattern: str
    description: str
    fields: tuple[Field, ...] = field(default_factory=tuple)


def _id(p: str) -> Field:
    return Field("id", "string", "Unique id.", True, pattern=p)


TEXT = Field("text", "string", "Statement in plain words.", True)
CASE: tuple[NodeKind, ...] = (
    NodeKind("assumptions", r"^AS\d+$", "Assumptions the argument depends on.", (_id(r"^AS\d+$"), TEXT)),
    NodeKind("contexts", r"^C\d+$", "Context nodes.", (
        _id(r"^C\d+$"), TEXT, Field("evidence", "ids", "Evidence items that define the context."))),
    NodeKind("strategies", r"^S\d+$", "Strategy nodes.", (
        _id(r"^S\d+$"), TEXT, Field("evidence", "ids", "Evidence items behind the strategy."))),
    NodeKind("goals", r"^G\d+$", "Claims.", (
        _id(r"^G\d+$"), TEXT,
        Field("context", "ids", "Context ids."),
        Field("assumptions", "ids", "Assumption ids."),
        Field("supported_by", "ids", "Child goals or strategies."),
        Field("evidence", "ids", "Evidence item ids."),
        Field("undeveloped", "boolean", "True when the goal is deliberately not developed."),
        Field("undeveloped_reason", "string", "Why the goal is undeveloped."))),
    NodeKind("evidence", r"^EV-\d{2}$", "Evidence items (solutions).", (
        _id(r"^EV-\d{2}$"),
        Field("title", "string", "What the evidence is.", True),
        Field("status", "string", "open, partial or provided.", True, enum=EVIDENCE_STATUS),
        Field("rows", "ids", "Evidence table rows that motivate the item.", True),
        Field("decision_needed", "boolean", "A decision by the owner is needed first."),
        Field("optional", "boolean", "Item is optional for this case."),
        Field("note", "string", "Free note."),
        Field("artefact", "string", "Path of the artefact, relative to the repository root."))),
)
CASE_TOP_LEVEL: tuple[str, ...] = ("meta", "strategy_links") + tuple(k.key for k in CASE)
META_FIELDS: tuple[str, ...] = ("title", "version", "status", "evidence_table", "note")


def _type_ok(kind: str, v: Any) -> bool:
    if kind == "string": return isinstance(v, str)
    if kind == "boolean": return isinstance(v, bool)
    if kind == "ids": return isinstance(v, list) and all(isinstance(x, str) for x in v)
    raise ValueError(kind)


def case_conformance(case: Any) -> list[str]:
    """Return a list of contract violations for a loaded case (empty list means it conforms)."""
    if not isinstance(case, dict): return ["case is not a mapping"]
    errs = [f"unknown top level key {k!r}" for k in case if k not in CASE_TOP_LEVEL]
    for k in (case.get("meta") or {}):
        if k not in META_FIELDS: errs.append(f"meta: unknown field {k!r}")
    links = case.get("strategy_links") or {}
    if not isinstance(links, dict) or not all(isinstance(v, list) for v in links.values()):
        errs.append("strategy_links must map a strategy id to a list of goal ids")
    for kind in CASE:
        nodes = case.get(kind.key) or []
        if not isinstance(nodes, list):
            errs.append(f"{kind.key} must be a list"); continue
        spec = {f.name: f for f in kind.fields}
        for n in nodes:
            if not isinstance(n, dict):
                errs.append(f"{kind.key}: node is not a mapping"); continue
            nid = n.get("id", "?")
            for k, v in n.items():
                f = spec.get(k)
                if f is None: errs.append(f"{nid}: unknown field {k!r} for {kind.key}"); continue
                if not _type_ok(f.kind, v): errs.append(f"{nid}: field {k!r} must be {f.kind}")
                elif f.enum and v not in f.enum: errs.append(f"{nid}: field {k!r} value {v!r} not in {list(f.enum)}")
                elif f.pattern and isinstance(v, str) and not re.match(f.pattern, v):
                    errs.append(f"{nid}: field {k!r} value {v!r} does not match {f.pattern}")
            for f in kind.fields:
                if f.required and f.name not in n: errs.append(f"{nid}: missing required field {f.name!r}")
    return errs
