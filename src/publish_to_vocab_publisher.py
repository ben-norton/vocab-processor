"""Copy the data/ directory to the vocab-publisher repository (ben-norton/vocab-publisher).

Mirrors every file under data/ into the configured target data directory,
reporting each file as added, updated, or unchanged.  Files that exist only
in the target (e.g. manifest.ttl, config/glossaries.json, content/, glossaries/)
are never touched.

Safety net around each publish:
  1. Backup  — before anything is overwritten, the whole target data directory
               is copied to temp/publisher-data-backup-YYYYMMDD-HHMMSS/ in this
               project (gitignored).
  2. Verify  — the publisher is rebuilt and checked in its own directory
               (the parent of the target): `npm run index`, then
               `node scripts/verify-static.js`.
  3. Cleanup — if verification passes, the backup is deleted.  If it fails,
               the backup is kept, the exit code is 1, and --restore rolls the
               target back to it.

Default target: G:/repos/vocabularies/vocab-publisher/data

Usage:
    python src/publish_to_vocab_publisher.py
    python src/publish_to_vocab_publisher.py --dry-run
    python src/publish_to_vocab_publisher.py --no-verify     # keep backup; verify by hand
    python src/publish_to_vocab_publisher.py --restore       # roll back to the newest backup
    python src/publish_to_vocab_publisher.py --restore publisher-data-backup-20260930-141500
    python src/publish_to_vocab_publisher.py --clean-backups # delete every backup once verified
    python src/publish_to_vocab_publisher.py --target /path/to/other/vocab-publisher/data
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT       = Path(__file__).resolve().parents[1]
SRC_DIR    = ROOT / "data"
DEFAULT_TARGET = Path(r"G:\repos\vocabularies\vocab-publisher\data")
BACKUP_DIR = ROOT / "temp"
BACKUP_PREFIX = "publisher-data-backup-"

# Run in the publisher project (the target's parent) after copying.
VERIFY_STEPS = [
    ["npm", "run", "index"],
    ["node", "scripts/verify-static.js"],
]


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


# ---------------------------------------------------------------------------
# Backups
# ---------------------------------------------------------------------------

def list_backups() -> list[Path]:
    """Existing backups, oldest first (the timestamp sorts lexically)."""
    if not BACKUP_DIR.is_dir():
        return []
    return sorted(p for p in BACKUP_DIR.glob(BACKUP_PREFIX + "*") if p.is_dir())


def make_backup(dst: Path) -> Path:
    """Copy the whole target data directory to a timestamped backup folder."""
    backup = BACKUP_DIR / (BACKUP_PREFIX + datetime.now().strftime("%Y%m%d-%H%M%S"))
    shutil.copytree(dst, backup)
    return backup


def restore_backup(backup: Path, dst: Path) -> None:
    """Make dst an exact copy of backup: files added since are removed."""
    for f in sorted(dst.rglob("*"), reverse=True):
        rel = f.relative_to(dst)
        if f.is_file() and not (backup / rel).is_file():
            f.unlink()
            print(f"[removed]  {rel}")
        elif f.is_dir() and not (backup / rel).is_dir() and not any(f.iterdir()):
            f.rmdir()
    for f in sorted(backup.rglob("*")):
        if f.is_file():
            rel = f.relative_to(backup)
            target = dst / rel
            if not target.is_file() or target.read_bytes() != f.read_bytes():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target)
                print(f"[restored] {rel}")


def delete_backup(backup: Path) -> None:
    shutil.rmtree(backup)
    if BACKUP_DIR.is_dir() and not any(BACKUP_DIR.iterdir()):
        BACKUP_DIR.rmdir()


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_publisher(publisher_root: Path) -> bool:
    """Rebuild the publisher's generated data and run its static checks."""
    for step in VERIFY_STEPS:
        exe = shutil.which(step[0])  # resolves npm.cmd on Windows
        if exe is None:
            print(f"ERROR: {step[0]} not found on PATH", file=sys.stderr)
            return False
        print(f"\n$ {' '.join(step)}   (in {publisher_root})")
        result = subprocess.run([exe, *step[1:]], cwd=publisher_root)
        if result.returncode != 0:
            print(f"FAILED: {' '.join(step)} exited {result.returncode}", file=sys.stderr)
            return False
    return True


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_restore(name: str, dst: Path, verify: bool) -> int:
    backups = list_backups()
    if not backups:
        print("No backups found in", BACKUP_DIR, file=sys.stderr)
        return 1
    backup = BACKUP_DIR / name if name else backups[-1]
    if not backup.is_dir():
        print(f"ERROR: backup not found: {backup}", file=sys.stderr)
        return 1
    print(f"Restoring {dst} from {backup.name}\n")
    restore_backup(backup, dst)
    # Regenerate the publisher's derived JSON from the restored data.
    if verify and not verify_publisher(dst.parent):
        print(f"\nRestored, but verification failed. Backup kept: {backup}")
        return 1
    print(f"\nRestore complete. Backup kept at {backup} — delete it with --clean-backups.")
    return 0


def cmd_clean() -> int:
    backups = list_backups()
    for b in backups:
        delete_backup(b)
        print(f"[deleted] {b.name}")
    print(f"Deleted {len(backups)} backup(s)." if backups else "No backups to delete.")
    return 0


def cmd_publish(src: Path, dst: Path, dry_run: bool, verify: bool) -> int:
    mode = "[dry-run] " if dry_run else ""
    print(f"{mode}Source : {src}")
    print(f"{mode}Target : {dst}")
    print()

    changed = sync(src, dst, dry_run=True)
    n_changed = len(changed["added"]) + len(changed["updated"])

    backup = None
    if not dry_run and n_changed:
        backup = make_backup(dst)
        print(f"Backup : {backup}\n")

    stats = sync(src, dst, dry_run=dry_run) if not dry_run else changed

    tag_label = {"added": "added  ", "updated": "updated", "unchanged": "ok     "}
    for tag in ("added", "updated", "unchanged"):
        for rel in stats[tag]:
            print(f"[{tag_label[tag]}]  {rel}")

    n_added    = len(stats["added"])
    n_updated  = len(stats["updated"])
    n_unchanged = len(stats["unchanged"])

    print()
    if dry_run:
        print(
            f"Dry-run complete: {n_added} to add, {n_updated} to update, "
            f"{n_unchanged} already up to date."
        )
        return 0
    if not n_changed:
        print("All files already up to date — nothing to copy.")
        return 0

    print(
        f"Done: {n_added} added, {n_updated} updated, "
        f"{n_unchanged} already up to date."
    )

    if not verify:
        print(f"\nVerification skipped. Backup kept: {backup}")
        print("Once verified, delete it with --clean-backups (or roll back with --restore).")
        return 0

    if verify_publisher(dst.parent):
        delete_backup(backup)
        print(f"\nVerification passed — backup {backup.name} deleted.")
        return 0

    print(f"\nVerification FAILED — backup kept: {backup}", file=sys.stderr)
    print(f"Roll back with:  python src/publish_to_vocab_publisher.py --restore {backup.name}",
          file=sys.stderr)
    return 1


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
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Skip the publisher rebuild/checks and keep the backup.",
    )
    parser.add_argument(
        "--restore",
        nargs="?",
        const="",
        metavar="BACKUP",
        help="Restore the target from a backup folder name (default: the newest).",
    )
    parser.add_argument(
        "--clean-backups",
        action="store_true",
        help=f"Delete every backup in {BACKUP_DIR}.",
    )
    args = parser.parse_args()

    src = SRC_DIR
    dst = Path(args.target)

    if args.clean_backups:
        sys.exit(cmd_clean())

    if not dst.is_dir():
        print(f"ERROR: target directory not found: {dst}", file=sys.stderr)
        sys.exit(1)

    if args.restore is not None:
        sys.exit(cmd_restore(args.restore, dst, verify=not args.no_verify))

    if not src.is_dir():
        print(f"ERROR: source directory not found: {src}", file=sys.stderr)
        sys.exit(1)

    sys.exit(cmd_publish(src, dst, dry_run=args.dry_run, verify=not args.no_verify))


if __name__ == "__main__":
    main()
