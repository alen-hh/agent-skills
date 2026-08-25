#!/usr/bin/env python3
"""Query the arXiv Atom API and print JSON. Stdlib only.

Examples:
  python3 query.py lookup 1706.03762
  python3 query.py lookup 1706.03762v1 hep-ex/0307015
  python3 query.py search "mixture of experts" --cat cs.LG --max 5 --sort submittedDate
  python3 query.py search --author Vaswani --title attention --cat cs.CL
  python3 query.py search --raw 'ti:"graph neural network" AND cat:cs.LG'
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

API_URL = "https://export.arxiv.org/api/query"
API_URL_HTTP = "http://export.arxiv.org/api/query"
USER_AGENT = (
    "alen-hh-agent-skills-arxiv/1.0 "
    "(https://github.com/alen-hh/agent-skills; arXiv Atom API client)"
)
TIMEOUT_SECONDS = 30
RETRY_DELAY_SECONDS = 3
MAX_RESULTS_CAP = 100

ATOM = "{http://www.w3.org/2005/Atom}"
OPENSEARCH = "{http://a9.com/-/spec/opensearch/1.1/}"
ARXIV = "{http://arxiv.org/schemas/atom}"

ID_PREFIX_RE = re.compile(
    r"^(?:https?://(?:www\.)?arxiv\.org/(?:abs|pdf|html|src)/|arxiv:)",
    re.IGNORECASE,
)
VERSION_RE = re.compile(r"v(\d+)$")
NEW_ID_RE = re.compile(r"^\d{4}\.\d{4,5}(v\d+)?$")
OLD_ID_RE = re.compile(r"^[a-z-]+(?:\.[A-Z]{2})?/\d{7}(v\d+)?$")


def die(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def collapse(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def normalize_arxiv_id(raw: str) -> str:
    value = collapse(raw)
    value = ID_PREFIX_RE.sub("", value)
    if value.endswith(".pdf"):
        value = value[: -len(".pdf")]
    return value.strip("/")


def validate_arxiv_id(arxiv_id: str) -> str:
    arxiv_id = normalize_arxiv_id(arxiv_id)
    if not arxiv_id:
        die("Empty arXiv id.")
    if not (NEW_ID_RE.match(arxiv_id) or OLD_ID_RE.match(arxiv_id)):
        die(
            f"Unrecognized arXiv id '{arxiv_id}'. "
            "Expected YYMM.NNNNN (optionally vN) or an old id like hep-ex/0307015."
        )
    return arxiv_id


def field_clause(prefix: str, value: str) -> str:
    value = collapse(value)
    if not value:
        return ""
    if value.startswith(f"{prefix}:"):
        return value
    if " " in value and not (value.startswith('"') and value.endswith('"')):
        return f'{prefix}:"{value}"'
    return f"{prefix}:{value}"


def date_stamp(value: str, end_of_day: bool) -> str:
    value = collapse(value)
    for fmt, out in (
        ("%Y-%m-%d", True),
        ("%Y%m%d", True),
        ("%Y-%m-%dT%H:%M", False),
        ("%Y%m%d%H%M", False),
    ):
        try:
            parsed = datetime.strptime(value, fmt)
        except ValueError:
            continue
        if out and end_of_day:
            return parsed.strftime("%Y%m%d") + "2359"
        if out:
            return parsed.strftime("%Y%m%d") + "0000"
        return parsed.strftime("%Y%m%d%H%M")
    die(f"Invalid date '{value}'. Use YYYY-MM-DD or YYYYMMDDHHMM.")
    return ""  # unreachable


def submitted_date_clause(since: str | None, until: str | None) -> str:
    if not since and not until:
        return ""
    start = date_stamp(since, end_of_day=False) if since else "199108010000"
    end = (
        date_stamp(until, end_of_day=True)
        if until
        else datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    )
    return f"submittedDate:[{start} TO {end}]"


def combine_and(parts: list[str]) -> str:
    cleaned = [p for p in parts if p]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0]
    return " AND ".join(f"({p})" if " OR " in p or " AND " in p else p for p in cleaned)


def build_search_query(args: argparse.Namespace) -> str:
    if args.raw:
        return collapse(args.raw)

    parts: list[str] = []
    terms = collapse(" ".join(args.terms or []))
    if terms:
        parts.append(field_clause("all", terms) if args.field == "all" else field_clause(args.field, terms))
    if args.title:
        parts.append(field_clause("ti", args.title))
    if args.author:
        parts.append(field_clause("au", args.author))
    if args.abstract:
        parts.append(field_clause("abs", args.abstract))
    if args.comment:
        parts.append(field_clause("co", args.comment))
    if args.journal:
        parts.append(field_clause("jr", args.journal))
    if args.cat:
        cats = [field_clause("cat", c) for c in args.cat]
        parts.append(cats[0] if len(cats) == 1 else "(" + " OR ".join(cats) + ")")
    date_part = submitted_date_clause(args.since, args.until)
    if date_part:
        parts.append(date_part)

    query = combine_and(parts)
    if not query:
        die("Nothing to search. Pass keywords, --raw, or at least one field flag.")
    return query


def parse_entry_id(atom_id: str) -> tuple[str, str | None, str]:
    href = collapse(atom_id)
    abs_url = href.replace("http://", "https://", 1)
    arxiv_id = normalize_arxiv_id(abs_url)
    version = None
    match = VERSION_RE.search(arxiv_id)
    if match:
        version = match.group(0)
        canonical = arxiv_id[: match.start()]
    else:
        canonical = arxiv_id
    return canonical, version, f"https://arxiv.org/abs/{canonical}"


def text(el: ET.Element | None) -> str:
    if el is None or el.text is None:
        return ""
    return collapse(el.text)


def parse_entry(entry: ET.Element) -> dict[str, Any]:
    raw_id = text(entry.find(f"{ATOM}id"))
    title_el = entry.find(f"{ATOM}title")
    title = collapse(title_el.text if title_el is not None else "")
    if title == "Error":
        return {
            "error": True,
            "message": text(entry.find(f"{ATOM}summary")) or raw_id,
            "id": raw_id,
        }

    canonical, version, abs_url = parse_entry_id(raw_id)
    authors = []
    for author in entry.findall(f"{ATOM}author"):
        name = text(author.find(f"{ATOM}name"))
        affiliation = text(author.find(f"{ARXIV}affiliation"))
        item: dict[str, str] = {"name": name}
        if affiliation:
            item["affiliation"] = affiliation
        if name:
            authors.append(item)

    pdf_url = None
    doi_url = None
    html_abs = abs_url
    for link in entry.findall(f"{ATOM}link"):
        rel = link.get("rel", "")
        title_attr = link.get("title", "")
        href = link.get("href", "")
        if rel == "alternate":
            html_abs = href.replace("http://", "https://", 1)
        elif title_attr == "pdf":
            pdf_url = href.replace("http://", "https://", 1)
        elif title_attr == "doi":
            doi_url = href

    categories = [
        cat.get("term", "")
        for cat in entry.findall(f"{ATOM}category")
        if cat.get("term")
    ]
    primary = entry.find(f"{ARXIV}primary_category")
    primary_category = primary.get("term") if primary is not None else (categories[0] if categories else "")

    return {
        "id": canonical,
        "version": version,
        "title": title,
        "authors": [a["name"] for a in authors],
        "author_details": authors,
        "summary": text(entry.find(f"{ATOM}summary")),
        "published": text(entry.find(f"{ATOM}published")),
        "updated": text(entry.find(f"{ATOM}updated")),
        "primary_category": primary_category,
        "categories": categories,
        "comment": text(entry.find(f"{ARXIV}comment")),
        "journal_ref": text(entry.find(f"{ARXIV}journal_ref")),
        "doi": text(entry.find(f"{ARXIV}doi")),
        "abs_url": html_abs or abs_url,
        "pdf_url": pdf_url or f"https://arxiv.org/pdf/{canonical}",
        "doi_url": doi_url,
    }


def parse_feed(xml_bytes: bytes) -> dict[str, Any]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        die(f"Failed to parse Atom XML: {exc}")

    entries = [parse_entry(el) for el in root.findall(f"{ATOM}entry")]
    errors = [e for e in entries if e.get("error")]
    papers = [e for e in entries if not e.get("error")]
    total = text(root.find(f"{OPENSEARCH}totalResults"))
    start_index = text(root.find(f"{OPENSEARCH}startIndex"))
    per_page = text(root.find(f"{OPENSEARCH}itemsPerPage"))
    return {
        "total_results": int(total or 0),
        "start_index": int(start_index or 0),
        "items_per_page": int(per_page or len(papers)),
        "updated": text(root.find(f"{ATOM}updated")),
        "errors": [{"message": e["message"], "id": e.get("id", "")} for e in errors],
        "papers": papers,
    }


def _ssl_failure(exc: BaseException) -> bool:
    message = str(exc).lower()
    return isinstance(exc, ssl.SSLError) or "certificate" in message or "ssl" in message


def fetch_curl(url: str) -> bytes:
    curl = shutil.which("curl")
    if not curl:
        raise FileNotFoundError("curl is not available")
    result = subprocess.run(
        [
            curl,
            "-fsSL",
            "-A",
            USER_AGENT,
            "--max-time",
            str(TIMEOUT_SECONDS),
            url,
        ],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip() or f"curl exit {result.returncode}")
    return result.stdout


def fetch_urllib(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        return response.read()


def fetch_urllib_with_retries(url: str, retries: int) -> bytes:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return fetch_urllib(url)
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code in {429, 500, 502, 503, 504} and attempt < retries:
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            body = ""
            try:
                body = exc.read().decode("utf-8", errors="replace")[:400]
            except Exception:
                pass
            die(f"arXiv API HTTP {exc.code}: {exc.reason}. {body}".strip())
        except Exception as exc:
            last_error = exc
            if _ssl_failure(exc) or attempt >= retries:
                raise
            time.sleep(RETRY_DELAY_SECONDS)
    raise last_error or RuntimeError("unreachable")


def fetch(params: dict[str, str], retries: int = 1) -> bytes:
    query = urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)
    https_url = f"{API_URL}?{query}"
    errors: list[str] = []

    try:
        return fetch_urllib_with_retries(https_url, retries)
    except Exception as exc:
        errors.append(f"urllib https: {exc}")

    try:
        return fetch_curl(https_url)
    except Exception as exc:
        errors.append(f"curl https: {exc}")

    try:
        return fetch_urllib_with_retries(f"{API_URL_HTTP}?{query}", retries)
    except Exception as exc:
        errors.append(f"urllib http: {exc}")

    die("Failed to reach arXiv API. " + " | ".join(errors))
    return b""


def query_api(
    *,
    search_query: str = "",
    id_list: list[str] | None = None,
    start: int = 0,
    max_results: int = 8,
    sort_by: str = "relevance",
    sort_order: str = "descending",
) -> dict[str, Any]:
    if max_results < 1:
        die("--max must be >= 1")
    if max_results > MAX_RESULTS_CAP:
        die(f"--max is capped at {MAX_RESULTS_CAP} for interactive lookup. Narrow the query instead.")
    if start < 0:
        die("--start must be >= 0")

    params = {
        "start": str(start),
        "max_results": str(max_results),
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    if search_query:
        params["search_query"] = search_query
    if id_list:
        params["id_list"] = ",".join(id_list)

    payload = parse_feed(fetch(params))
    payload["request"] = {
        "search_query": search_query,
        "id_list": id_list or [],
        "start": start,
        "max_results": max_results,
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    return payload


def add_common_flags(parser: argparse.ArgumentParser, *, max_default: int | None = 8) -> None:
    parser.add_argument("--start", type=int, default=0, help="0-based offset (default: 0)")
    parser.add_argument(
        "--max",
        type=int,
        default=max_default,
        help="Number of results (default: 8 for search, one per id for lookup; cap: 100)",
    )
    parser.add_argument(
        "--sort",
        choices=("relevance", "lastUpdatedDate", "submittedDate"),
        default="relevance",
        help="Sort field (default: relevance)",
    )
    parser.add_argument(
        "--order",
        choices=("ascending", "descending"),
        default="descending",
        help="Sort direction (default: descending)",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query the arXiv Atom API and print JSON.")
    sub = parser.add_subparsers(dest="command", required=True)

    lookup = sub.add_parser("lookup", help="Fetch papers by arXiv id")
    lookup.add_argument("ids", nargs="+", help="arXiv ids, abs URLs, or arXiv:YYMM.NNNNN")
    add_common_flags(lookup, max_default=None)

    search = sub.add_parser("search", help="Search by keywords and fields")
    search.add_argument("terms", nargs="*", help="Free-text terms (default field: all)")
    search.add_argument("--raw", help="Raw search_query; overrides other field flags")
    search.add_argument(
        "--field",
        choices=("all", "ti", "au", "abs", "co", "jr", "cat"),
        default="all",
        help="Field for positional terms (default: all)",
    )
    search.add_argument("--title", help="Title query (ti:)")
    search.add_argument("--author", help="Author query (au:)")
    search.add_argument("--abstract", help="Abstract query (abs:)")
    search.add_argument("--comment", help="Comment query (co:)")
    search.add_argument("--journal", help="Journal reference query (jr:)")
    search.add_argument("--cat", action="append", default=[], help="Category id; repeat to OR")
    search.add_argument("--since", help="submittedDate lower bound (YYYY-MM-DD)")
    search.add_argument("--until", help="submittedDate upper bound (YYYY-MM-DD)")
    add_common_flags(search)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "lookup":
        ids = [validate_arxiv_id(i) for i in args.ids]
        max_results = len(ids) if args.max is None else max(args.max, len(ids))
        result = query_api(
            id_list=ids,
            start=args.start,
            max_results=max_results,
            sort_by=args.sort,
            sort_order=args.order,
        )
    else:
        result = query_api(
            search_query=build_search_query(args),
            start=args.start,
            max_results=args.max,
            sort_by=args.sort,
            sort_order=args.order,
        )

    if result["errors"] and not result["papers"]:
        messages = "; ".join(e["message"] for e in result["errors"])
        die(f"arXiv API error: {messages}")

    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
