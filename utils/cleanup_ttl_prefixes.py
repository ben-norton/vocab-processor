"""Remove unused @prefix declarations from Turtle (.ttl) files.

Scans each *.ttl in data/vocabs/ (or a given list of paths), identifies every
@prefix declaration whose prefix token does not appear as a CURIE in the file
body, and rewrites the file without those lines.

Usage:
    # Process all files in data/vocabs/
    python utils/cleanup_ttl_prefixes.py

    # Dry-run: report only, no writes
    python utils/cleanup_ttl_prefixes.py --dry-run

    # Target specific files
    python utils/cleanup_ttl_prefixes.py data/vocabs/aggregate-form.ttl

Dependencies: none (stdlib only).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT    = Path(__file__).resolve().parents[1]
TTL_DIR = ROOT / "data" / "vocabs"

# Matches a single @prefix declaration line (with any internal whitespace).
# Group 1 = prefix name (e.g. "owl"), Group 2 = full namespace IRI.
_PREFIX_LINE = re.compile(
    r'^@prefix\s+(\w+):\s+<([^>]*)>\s*\.\s*$',
    re.IGNORECASE,
)

# A CURIE use: word-boundary + prefix + colon + at least one non-space,
# non-slash char (ensures we are not matching inside a URI path like http://...).
_CURIE_USE = re.compile(r'\b{prefix}:[^\s/<]')


def _is_prefix_used(prefix: str, body: str) -> bool:
    """Return True if `prefix:localname` appears anywhere in body."""
    return bool(_CURIE_USE.pattern.replace("{prefix}", re.escape(prefix))
                and re.search(r'\b' + re.escape(prefix) + r':[^\s/<]', body))


def analyse(text: str) -> tuple[list[str], list[str]]:
    """Return (all_declared_prefixes, unused_prefixes) for the TTL text."""
    lines = text.splitlines()
    declared: list[str] = []

    # Strip out every @prefix line to form the body we'll search in.
    body_lines: list[str] = []
    for line in lines:
        m = _PREFIX_LINE.match(line)
        if m:
            declared.append(m.group(1))
        else:
            body_lines.append(line)

    body = "\n".join(body_lines)
    unused = [p for p in declared if not _is_prefix_used(p, body)]
    return declared, unused


def clean_text(text: str, unused: set[str]) -> str:
    """Remove @prefix lines for the given set of prefix names and tidy whitespace."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        m = _PREFIX_LINE.match(line.rstrip("\r\n"))
        if m and m.group(1) in unused:
            continue
        out.append(line)

    cleaned = "".join(out)
    # Collapse runs of 3+ blank lines left behind by removed declarations.
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned


def process_file(path: Path, dry_run: bool) -> tuple[list[str], bool]:
    """Analyse and optionally rewrite one TTL file.

    Returns (removed_prefixes, file_was_written).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"  ERROR reading {path}: {exc}", file=sys.stderr)
        return [], False

    _, unused = analyse(text)
    if not unused:
        return [], False

    cleaned = clean_text(text, set(unused))

    if not dry_run:
        try:
            path.write_text(cleaned, encoding="utf-8")
        except OSError as exc:
            print(f"  ERROR writing {path}: {exc}", file=sys.stderr)
            return unused, False
        return unused, True

    return unused, False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Remove unused @prefix declarations from Turtle files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="TTL files to process (default: all *.ttl in data/vocabs/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report unused prefixes without modifying any files.",
    )
    args = parser.parse_args()

    paths: list[Path] = (
        [Path(f) for f in args.files]
        if args.files
        else sorted(TTL_DIR.glob("*.ttl"))
    )

    if not paths:
        print("No TTL files found.")
        sys.exit(0)

    name_w = max(len(str(p.relative_to(ROOT))) for p in paths)
    total_files_changed = 0
    total_prefixes_removed = 0

    for path in paths:
        removed, written = process_file(path, dry_run=args.dry_run)
        rel = str(path.relative_to(ROOT))

        if removed:
            tag = "dry-run" if args.dry_run else "cleaned"
            print(f"[{tag}]  {rel:<{name_w}}  removed: {', '.join(sorted(removed))}")
            total_prefixes_removed += len(removed)
            if written:
                total_files_changed += 1
        else:
            print(f"[ok]     {rel:<{name_w}}")

    print()
    if total_prefixes_removed:
        if args.dry_run:
            print(
                f"Would remove {total_prefixes_removed} unused prefix declaration(s) "
                f"from {len([p for p in paths if analyse(p.read_text(encoding='utf-8'))[1]])} file(s)."
            )
        else:
            print(
                f"Removed {total_prefixes_removed} unused prefix declaration(s) "
                f"from {total_files_changed} file(s)."
            )
    else:
        print("All files clean — no unused prefixes found.")


if __name__ == "__main__":
    main()
