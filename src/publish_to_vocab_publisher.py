"""Copy the data/ directory to the vocab-publisher repository (ben-norton/vocab-publisher).

Mirrors every file under data/ into the configured target data directory,
reporting each file as added, updated, or unchanged.  Files that exist only
in the target (e.g. manifest.ttl, config/glossaries.json, content/, glossaries/)
are never touched.

Default target: G:/webserver/Apache/htdocs-apps/geoapis-htdocs/vocab-publisher/data

Usage:
    python utils/publish_to_vocab_publisher.py
    python utils/publish_to_vocab_publisher.py --dry-run
    python utils/publish_to_vocab_publisher.py --target /path/to/other/vocab-publisher/data
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT       = Path(__file__).resolve().parents[1]
SRC_DIR    = ROOT / "data"
DEFAULT_TARGET = Path(r"G:\webserver\Apache\htdocs-apps\geoapis-htdocs\vocab-publisher\data")


def sync(src: Path, dst: Path, dry_run: bool) -> dict[str, list[Path]]:
    """Copy files from src to dst, skipping files whose content is identical.

    Returns a dict with keys 'added', 'updated', 'unchanged'.
    """
    stats: dict[str, list[Path]] = {"added": [], "updated": [], "unchanged": []}

    for src_file in sorted(src.rglob("*")):
        if not src_file.is_file():
            continue

        rel      = src_file.relative_to(src)
        dst_file = dst / rel

        if dst_file.exists():
            if src_file.read_bytes() == dst_file.read_bytes():
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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Copy data/ to the vocab-publisher repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--target",
        metavar="DIR",
        default=str(DEFAULT_TARGET),
        help=f"Destination data directory (default: {DEFAULT_TARGET})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be copied without writing any files.",
    )
    args = parser.parse_args()

    src = SRC_DIR
    dst = Path(args.target)

    if not src.is_dir():
        print(f"ERROR: source directory not found: {src}", file=sys.stderr)
        sys.exit(1)
    if not dst.is_dir():
        print(f"ERROR: target directory not found: {dst}", file=sys.stderr)
        sys.exit(1)

    mode = "[dry-run] " if args.dry_run else ""
    print(f"{mode}Source : {src}")
    print(f"{mode}Target : {dst}")
    print()

    stats = sync(src, dst, dry_run=args.dry_run)

    tag_label = {"added": "added  ", "updated": "updated", "unchanged": "ok     "}
    for tag in ("added", "updated", "unchanged"):
        for rel in stats[tag]:
            print(f"[{tag_label[tag]}]  {rel}")

    n_added    = len(stats["added"])
    n_updated  = len(stats["updated"])
    n_unchanged = len(stats["unchanged"])
    n_changed  = n_added + n_updated

    print()
    if args.dry_run:
        print(
            f"Dry-run complete: {n_added} to add, {n_updated} to update, "
            f"{n_unchanged} already up to date."
        )
    elif n_changed:
        print(
            f"Done: {n_added} added, {n_updated} updated, "
            f"{n_unchanged} already up to date."
        )
    else:
        print("All files already up to date — nothing to copy.")


if __name__ == "__main__":
    main()
