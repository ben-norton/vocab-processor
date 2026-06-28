"""Validate SKOS Turtle vocabulary files in data/vocabs/.

Checks performed for each .ttl file:
  1. Turtle syntax  — rdflib can parse the file without error
  2. ConceptScheme  — exactly one skos:ConceptScheme is declared
  3. Scheme props   — required dcterms/skos metadata is present
  4. Concept props  — every skos:Concept has prefLabel + definition
  5. skos:inScheme  — every Concept is linked to the ConceptScheme
  6. Top concept    — hasTopConcept / topConceptOf are bidirectionally consistent
  7. IRI prefix     — concept IRIs share a common base with the scheme IRI
  8. Duplicate labels — no two concepts share the same prefLabel in the same language

Run from the project root:
    python utils/validate-ttl.py [path ...]

If no paths are given, all *.ttl files in data/vocabs/ are validated.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF, SKOS

# ---------------------------------------------------------------------------
# Namespace shorthands
# ---------------------------------------------------------------------------

DCAT = Namespace("http://www.w3.org/ns/dcat#")
SCHEMA = Namespace("https://schema.org/")
REG = Namespace("http://purl.org/linked-data/registry#")

# ---------------------------------------------------------------------------
# Required properties on the ConceptScheme
# ---------------------------------------------------------------------------

REQUIRED_SCHEME_PROPS: list[tuple[str, URIRef]] = [
    ("skos:prefLabel",      SKOS.prefLabel),
    ("dcterms:title",       DCTERMS.title),
    ("skos:definition",     SKOS.definition),
    ("dcterms:description", DCTERMS.description),
    ("dcterms:created",     DCTERMS.created),
    ("dcterms:modified",    DCTERMS.modified),
    ("dcterms:publisher",   DCTERMS.publisher),
    ("dcterms:creator",     DCTERMS.creator),
    ("reg:status",          REG.status),
]

# Required properties on every skos:Concept
REQUIRED_CONCEPT_PROPS: list[tuple[str, URIRef]] = [
    ("skos:prefLabel",  SKOS.prefLabel),
    ("skos:definition", SKOS.definition),
    ("skos:inScheme",   SKOS.inScheme),
    ("reg:status",      REG.status),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ANSI_RED    = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN  = "\033[32m"
ANSI_RESET  = "\033[0m"
ANSI_BOLD   = "\033[1m"

_use_color = sys.stdout.isatty()


def _c(text: str, code: str) -> str:
    return f"{code}{text}{ANSI_RESET}" if _use_color else text


def red(t: str) -> str:    return _c(t, ANSI_RED)
def yellow(t: str) -> str: return _c(t, ANSI_YELLOW)
def green(t: str) -> str:  return _c(t, ANSI_GREEN)
def bold(t: str) -> str:   return _c(t, ANSI_BOLD)


class Report:
    """Accumulates errors and warnings for a single file."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.errors:   list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors

    def print(self) -> None:
        status = green("PASS") if self.ok else red("FAIL")
        header = f"{bold(self.path.name)}  [{status}]"
        print(header)
        for e in self.errors:
            print(f"  {red('ERROR')}  {e}")
        for w in self.warnings:
            print(f"  {yellow('WARN')}   {w}")
        if self.ok and not self.warnings:
            print(f"  {green('All checks passed.')}")
        print()


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_syntax(path: Path, report: Report) -> Graph | None:
    """Parse the file; return the graph or None on failure."""
    g = Graph()
    try:
        g.parse(str(path), format="turtle")
        return g
    except Exception as exc:  # noqa: BLE001
        report.error(f"Turtle parse error: {exc}")
        return None


def check_concept_scheme(g: Graph, report: Report) -> URIRef | None:
    """Exactly one skos:ConceptScheme must exist; return its IRI."""
    schemes = list(g.subjects(RDF.type, SKOS.ConceptScheme))
    if not schemes:
        report.error("No skos:ConceptScheme found.")
        return None
    if len(schemes) > 1:
        report.error(f"Multiple skos:ConceptScheme subjects: {schemes}")
    return URIRef(schemes[0])


def check_scheme_properties(
    g: Graph, scheme: URIRef, report: Report
) -> None:
    """Required metadata must be present on the ConceptScheme."""
    for label, prop in REQUIRED_SCHEME_PROPS:
        if not any(True for _ in g.objects(scheme, prop)):
            report.error(f"ConceptScheme missing {label}")


def check_concepts(
    g: Graph, scheme: URIRef, report: Report
) -> list[URIRef]:
    """Return all skos:Concept subjects; check required properties."""
    concepts = list(g.subjects(RDF.type, SKOS.Concept))
    if not concepts:
        report.warn("No skos:Concept instances found.")
        return []

    for concept in concepts:
        short = f"<{concept}>"
        for label, prop in REQUIRED_CONCEPT_PROPS:
            if not any(True for _ in g.objects(concept, prop)):
                report.error(f"Concept {short} missing {label}")

    return concepts


def check_in_scheme(
    g: Graph, scheme: URIRef, concepts: list[URIRef], report: Report
) -> None:
    """Every Concept's skos:inScheme must point to the declared scheme."""
    for concept in concepts:
        in_schemes = set(g.objects(concept, SKOS.inScheme))
        if scheme not in in_schemes:
            others = ", ".join(f"<{s}>" for s in in_schemes) or "(none)"
            report.error(
                f"<{concept}> skos:inScheme does not reference the scheme IRI. "
                f"Found: {others}"
            )


def check_top_concepts(
    g: Graph, scheme: URIRef, concepts: list[URIRef], report: Report
) -> None:
    """hasTopConcept / topConceptOf must be bidirectionally consistent."""
    has_top = set(g.objects(scheme, SKOS.hasTopConcept))
    top_of  = set(g.subjects(SKOS.topConceptOf, scheme))

    for c in has_top - top_of:
        report.warn(
            f"<{c}> listed in skos:hasTopConcept but missing "
            "skos:topConceptOf back-link."
        )
    for c in top_of - has_top:
        report.warn(
            f"<{c}> has skos:topConceptOf but is not listed in "
            "skos:hasTopConcept on the scheme."
        )

    concept_set = set(concepts)
    for c in has_top:
        if c not in concept_set:
            report.error(
                f"<{c}> is in skos:hasTopConcept but is not typed "
                "as skos:Concept."
            )


def check_iri_consistency(
    g: Graph, scheme: URIRef, concepts: list[URIRef], report: Report
) -> None:
    """Concept IRIs should share a common base prefix with the scheme IRI."""
    scheme_str = str(scheme).rstrip("/")
    mismatched = [
        c for c in concepts
        if not str(c).startswith(scheme_str)
    ]
    # Normalise http/https and retry before flagging
    def normalise(s: str) -> str:
        return s.replace("https://", "http://")

    mismatched_strict = [
        c for c in mismatched
        if not normalise(str(c)).startswith(normalise(scheme_str))
    ]
    if mismatched and not mismatched_strict:
        report.warn(
            f"{len(mismatched)} concept IRI(s) differ from the scheme only "
            "in http vs https scheme. Consider normalising to https://."
        )
    for c in mismatched_strict:
        report.warn(
            f"<{c}> IRI does not begin with scheme base <{scheme_str}/>"
        )


def check_duplicate_labels(
    g: Graph, concepts: list[URIRef], report: Report
) -> None:
    """No two concepts should share the same prefLabel in the same language."""
    seen: dict[tuple[str, str], list[URIRef]] = defaultdict(list)
    for concept in concepts:
        for label in g.objects(concept, SKOS.prefLabel):
            key = (str(label).lower(), getattr(label, "language", "") or "")
            seen[key].append(concept)

    for (label_text, lang), owners in seen.items():
        if len(owners) > 1:
            lang_tag = f"@{lang}" if lang else ""
            owner_list = ", ".join(f"<{c}>" for c in owners)
            report.error(
                f'Duplicate skos:prefLabel "{label_text}"{lang_tag} on: {owner_list}'
            )


# ---------------------------------------------------------------------------
# Top-level runner
# ---------------------------------------------------------------------------

def validate_file(path: Path) -> Report:
    report = Report(path)

    g = check_syntax(path, report)
    if g is None:
        return report  # cannot proceed without a valid graph

    scheme = check_concept_scheme(g, report)
    if scheme is None:
        return report

    check_scheme_properties(g, scheme, report)
    concepts = check_concepts(g, scheme, report)
    check_in_scheme(g, scheme, concepts, report)
    check_top_concepts(g, scheme, concepts, report)
    check_iri_consistency(g, scheme, concepts, report)
    check_duplicate_labels(g, concepts, report)

    return report


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parents[1]
    default_dir = root / "data" / "vocabs"

    if argv:
        paths = [Path(p) for p in argv]
    else:
        paths = sorted(default_dir.glob("*.ttl"))

    if not paths:
        print(f"No .ttl files found in {default_dir}")
        return 1

    reports = [validate_file(p) for p in paths]

    print()
    for r in reports:
        r.print()

    total   = len(reports)
    passing = sum(1 for r in reports if r.ok)
    failing = total - passing

    summary = f"Results: {passing}/{total} passed"
    if failing:
        print(red(summary + f", {failing} failed"))
        return 1
    print(green(summary))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
