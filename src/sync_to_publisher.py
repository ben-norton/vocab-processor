"""One-way synchronization of data/ into the vocab-publisher repository.

The publisher location is read from the `.env` file in the project root:

    VOCAB_PUBLISHER_PATH=G:\\repos\\vocabularies\\vocab-publisher

`VOCAB_PUBLISHER_PATH` points at the vocab-publisher repository root; the
target directory is `<VOCAB_PUBLISHER_PATH>/data`.  Set
`VOCAB_PUBLISHER_DATA_DIR` instead to name that data directory explicitly.
Real environment variables take precedence over the `.env` file.

Synchronization is strictly one way — data/ (source) overwrites the publisher
copy (target).  Nothing is ever read back.  Files that exist only in the target
(manifest.ttl, content/, config/glossaries.json, ...) are left alone unless
`--delete` is given.

Usage:
    python src/sync_to_publisher.py                      # whole data/ tree
    python src/sync_to_publisher.py --dry-run            # preview only
    python src/sync_to_publisher.py --only vocabs        # just data/vocabs/
    python src/sync_to_publisher.py --glossary gcdm      # just data/glossaries/gcdm/
    python src/sync_to_publisher.py --vocab hazard-type  # just data/vocabs/hazard-type*.ttl
    python src/sync_to_publisher.py --only glossaries/kos-terms/kos-terms.ttl
    python src/sync_to_publisher.py --force              # recopy even if identical
    python src/sync_to_publisher.py --only vocabs --delete   # prune target extras in scope
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path

ROOT     = Path(__file__).resolve().parents[1]
SRC_DIR  = ROOT / "data"
ENV_FILE = ROOT / ".env"

ENV_REPO_KEY = "VOCAB_PUBLISHER_PATH"
ENV_DATA_KEY = "VOCAB_PUBLISHER_DATA_DIR"


# ── .env handling ──────────────────────────────────────────────────────

def load_dotenv(path: Path) -> dict[str, str]:
    """Parse a minimal .env file into a dict.

    Supports `KEY=value`, `export KEY=value`, `#` comments and quoted values.
    Values are taken literally — no escape or variable expansion — so Windows
    paths with backslashes work unquoted.
    """
    values: dict[str, str] = {}
    if not path.is_file():
        return values

    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key.startswith("export "):
            key = key[len("export "):].strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        if key:
            values[key] = value
    return values


def resolve_target() -> Path:
    """Return the publisher data directory from the environment or .env."""
    env = load_dotenv(ENV_FILE)

    # Real environment variables win over the .env file.
    data_dir = os.environ.get(ENV_DATA_KEY) or env.get(ENV_DATA_KEY)
    if data_dir:
        return Path(data_dir.strip()).expanduser()

    repo = os.environ.get(ENV_REPO_KEY) or env.get(ENV_REPO_KEY)
    if repo:
        return Path(repo.strip()).expanduser() / "data"

    print(
        f"ERROR: no publisher path configured.\n"
        f"  Add {ENV_REPO_KEY} to {ENV_FILE} (see .env.example), e.g.\n"
        f"    {ENV_REPO_KEY}=G:\\repos\\vocabularies\\vocab-publisher\n"
        f"  or set {ENV_DATA_KEY} to the publisher's data directory directly.",
        file=sys.stderr,
    )
    sys.exit(1)


# ── scope selection ────────────────────────────────────────────────────

def resolve_scope(args: argparse.Namespace) -> Path:
    """Return the source path to synchronize — data/ itself, or a subpath."""
    if args.glossary:
        rel = Path("glossaries") / args.glossary
    elif args.vocab:
        name = args.vocab
        rel = Path("vocabs") / (name if name.endswith(".ttl") else f"{name}.ttl")
    elif args.only:
        rel = Path(args.only.replace("\\", "/"))
    else:
        return SRC_DIR

    if rel.is_absolute() or ".." in rel.parts:
        print(f"ERROR: scope must be a relative path inside data/: {rel}",
              file=sys.stderr)
        sys.exit(1)

    scope = SRC_DIR / rel
    if not scope.exists():
        available = ", ".join(
            sorted(p.name for p in SRC_DIR.iterdir() if p.is_dir())
        ) or "(none)"
        print(f"ERROR: not found in the source tree: {scope}", file=sys.stderr)
        print(f"  data/ contains: {available}", file=sys.stderr)
        sys.exit(1)
    return scope


def source_files(scope: Path) -> list[Path]:
    """Files to copy, as paths relative to data/."""
    if scope.is_file():
        return [scope.relative_to(SRC_DIR)]
    return sorted(
        p.relative_to(SRC_DIR) for p in scope.rglob("*") if p.is_file()
    )


# ── synchronization ────────────────────────────────────────────────────

def sync(rels: list[Path], dst_root: Path, *, dry_run: bool,
         force: bool) -> dict[str, list[Path]]:
    """Copy each relative path from data/ into dst_root, overwriting.

    Returns a dict with keys 'added', 'updated', 'unchanged'.
    """
    stats: dict[str, list[Path]] = {"added": [], "updated": [], "unchanged": []}

    for rel in rels:
        src_file = SRC_DIR / rel
        dst_file = dst_root / rel

        if dst_file.exists():
            if not force and src_file.read_bytes() == dst_file.read_bytes():
                stats["unchanged"].append(rel)
                continue
            tag = "updated"
        else:
            tag = "added"

        stats[tag].append(rel)
        if not dry_run:
            dst_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_file, dst_file)

    return stats


def prune(scope: Path, dst_root: Path, dry_run: bool) -> list[Path]:
    """Delete target files inside the scope that have no source counterpart."""
    if scope.is_file():
        return []

    rel_scope = scope.relative_to(SRC_DIR)
    dst_scope = dst_root / rel_scope
    if not dst_scope.is_dir():
        return []

    removed: list[Path] = []
    for dst_file in sorted(dst_scope.rglob("*")):
        if not dst_file.is_file():
            continue
        rel = dst_file.relative_to(dst_root)
        if (SRC_DIR / rel).is_file():
            continue
        removed.append(rel)
        if not dry_run:
            dst_file.unlink()
    return removed


# ── CLI ────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="One-way sync of data/ into the vocab-publisher repository "
                    "(target read from .env).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    scope_group = parser.add_mutually_exclusive_group()
    scope_group.add_argument(
        "--only",
        metavar="SUBPATH",
        help="Limit the sync to a path under data/ — a directory or a single "
             "file (e.g. 'vocabs', 'glossaries/gcdm', "
             "'glossaries/kos-terms/kos-terms.ttl').",
    )
    scope_group.add_argument(
        "--glossary",
        metavar="SLUG",
        help="Limit the sync to data/glossaries/<SLUG>/.",
    )
    scope_group.add_argument(
        "--vocab",
        metavar="NAME",
        help="Limit the sync to a single data/vocabs/<NAME>.ttl "
             "(the .ttl extension is optional).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be copied or deleted without writing anything.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recopy every file in scope, even when the target is identical.",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Also delete target files inside the scope that no longer exist "
             "in data/. Off by default so publisher-only files (manifest.ttl, "
             "content/, ...) are preserved.",
    )
    args = parser.parse_args()

    if not SRC_DIR.is_dir():
        print(f"ERROR: source directory not found: {SRC_DIR}", file=sys.stderr)
        sys.exit(1)

    dst_root = resolve_target()
    if not dst_root.is_dir():
        print(f"ERROR: target directory not found: {dst_root}", file=sys.stderr)
        print(f"  Check {ENV_REPO_KEY} in {ENV_FILE}.", file=sys.stderr)
        sys.exit(1)

    scope = resolve_scope(args)
    rels  = source_files(scope)

    mode = "[dry-run] " if args.dry_run else ""
    print(f"{mode}Source : {scope}")
    print(f"{mode}Target : {dst_root / scope.relative_to(SRC_DIR)}")
    print(f"{mode}Files  : {len(rels)} in scope")
    print()

    if not rels:
        print("Nothing to synchronize — the scope contains no files.")
        return

    stats   = sync(rels, dst_root, dry_run=args.dry_run, force=args.force)
    deleted = prune(scope, dst_root, args.dry_run) if args.delete else []

    tag_label = {"added": "added  ", "updated": "updated", "unchanged": "ok     "}
    for tag in ("added", "updated", "unchanged"):
        for rel in stats[tag]:
            print(f"[{tag_label[tag]}]  {rel}")
    for rel in deleted:
        print(f"[deleted]  {rel}")

    n_added     = len(stats["added"])
    n_updated   = len(stats["updated"])
    n_unchanged = len(stats["unchanged"])
    n_deleted   = len(deleted)

    print()
    suffix = f", {n_deleted} to delete" if args.delete else ""
    if args.dry_run:
        print(f"Dry-run complete: {n_added} to add, {n_updated} to update, "
              f"{n_unchanged} already up to date{suffix}.")
    elif n_added or n_updated or n_deleted:
        done_suffix = f", {n_deleted} deleted" if args.delete else ""
        print(f"Done: {n_added} added, {n_updated} updated, "
              f"{n_unchanged} already up to date{done_suffix}.")
    else:
        print("All files already up to date — nothing to copy.")


if __name__ == "__main__":
    main()
