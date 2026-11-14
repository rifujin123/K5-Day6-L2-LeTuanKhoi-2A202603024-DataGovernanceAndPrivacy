"""Restore CRLF-converted fixtures only when LF bytes match the existing manifest.

    python -m tools.restore_fixture_newlines

Never changes manifest hashes or accepts an otherwise modified fixture.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


def main() -> int:
    restored = []
    unresolved = []
    pending = []
    root = Path("fixtures").resolve()
    for manifest in sorted(root.glob("*/manifest.csv")):
        for row in pd.read_csv(manifest, dtype=str).itertuples(index=False):
            path = (manifest.parent / row.path).resolve()
            if not path.is_relative_to(root) or not path.is_file():
                unresolved.append(str(path))
                continue
            original = path.read_bytes()
            if hashlib.sha256(original).hexdigest() == row.sha256:
                continue
            normalized = original.replace(b"\r\n", b"\n")
            if hashlib.sha256(normalized).hexdigest() != row.sha256:
                unresolved.append(str(path))
                continue
            pending.append((path, normalized))
    if unresolved:
        print("Unresolved fixture changes; no files written:")
        print("\n".join(unresolved))
        return 1
    for path, normalized in pending:
        path.write_bytes(normalized)
        restored.append(path)
    print(f"Restored {len(restored)} files to manifest-matching LF bytes; manifest hashes unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
