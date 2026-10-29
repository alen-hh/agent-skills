#!/usr/bin/env python3
"""Static checks for an html-prototype page. Does not open a browser."""

import re
import sys
from pathlib import Path

REMOTE_ASSET = re.compile(
    r"""<(?:script|link|img|iframe|source|video|audio)\b[^>]*\b(?:src|href)\s*=\s*['"]https?://""",
    re.IGNORECASE | re.DOTALL,
)
URL_FUNC = re.compile(r"""url\(\s*['"]?https?://""", re.IGNORECASE)
IMPORT_URL = re.compile(r"""@import\s+(?:url\()?['"]?https?://""", re.IGNORECASE)
MEDIA = re.compile(r"@media\b", re.IGNORECASE)
CONTAINER = re.compile(r"@container\b", re.IGNORECASE)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)

REQUIRED = (
    "animation: none",
    "transition: none",
    "1440px",
    "grid-template-rows: 1fr auto 1fr",
)


def check(path: Path) -> list[str]:
    errors: list[str] = []
    if not path.is_file():
        return [f"not a file: {path}"]
    if path.suffix.lower() not in {".html", ".htm"}:
        errors.append("expected an .html file")
    text = path.read_text(encoding="utf-8")
    # Comments may name @media while forbidding it. Judge the page, not the note.
    text = HTML_COMMENT.sub("", text)
    text = CSS_COMMENT.sub("", text)
    if MEDIA.search(text):
        errors.append("found @media; this prototype is desktop-only")
    if CONTAINER.search(text):
        errors.append("found @container; this prototype is desktop-only")
    if REMOTE_ASSET.search(text) or URL_FUNC.search(text) or IMPORT_URL.search(text):
        errors.append("found a remote asset URL; keep the file self-contained")
    for snippet in REQUIRED:
        if snippet not in text:
            errors.append(f"missing template rule: {snippet}")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(
            "usage: python3 check_page.py <screen.html> [more.html]",
            file=sys.stderr,
        )
        return 2
    failed = False
    for raw in argv[1:]:
        path = Path(raw)
        errors = check(path)
        if errors:
            failed = True
            print(f"fail {path}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"ok {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
