---
name: arxiv
description: Query arXiv e-prints via the official Atom API — search by title, author, abstract, category, or date, and look up papers by arXiv id. Use whenever the user mentions arXiv, arxiv.org, preprints, e-prints, paper lookup, ids like 1706.03762, or wants recent papers in cs.LG, cs.CL, hep-th, or other arXiv categories, even if they never say API.
---

# arXiv lookup

Search and fetch paper metadata from the [arXiv Atom API](https://info.arxiv.org/help/api/user-manual.html). Do not scrape `arxiv.org` HTML search pages. Do not invent titles, authors, or ids — always call the API.

The bundled script handles URL encoding, Atom XML, and id normalization. Run it from this skill's directory (or pass an absolute path to the script).

```bash
python3 scripts/query.py lookup 1706.03762
python3 scripts/query.py search "mixture of experts" --cat cs.LG --max 5 --sort submittedDate
```

## Choose a path

| User intent | What to run |
|-------------|-------------|
| An id, `arXiv:YYMM.NNNNN`, or `https://arxiv.org/abs/...` | `lookup` |
| "Papers about X", keywords, a title fragment | `search` with terms and optional `--cat` |
| "By Author", "Vaswani et al." | `search --author ...` |
| "Latest / this week / 2024" in a field | `search --sort submittedDate --since ...` plus `--cat` |
| Exact Boolean query | `search --raw 'ti:"..." AND cat:cs.LG'` |

If the user names a subject ("NLP", "vision", "hep-th") and you are unsure of the code, read [references/categories.md](references/categories.md) before searching. Do not load it for a plain id lookup.

## Build the query

Field prefixes (use these in `--raw`, or let the script add them from flags):

| Prefix | Field |
|--------|-------|
| `ti` | Title |
| `au` | Author |
| `abs` | Abstract |
| `co` | Comment |
| `jr` | Journal reference |
| `cat` | Subject category |
| `all` | All of the above |

Boolean operators: `AND`, `OR`, `ANDNOT`. Group with parentheses. Phrases go in double quotes.

Date filter (submission time, GMT): `submittedDate:[YYYYMMDDHHMM TO YYYYMMDDHHMM]`. The script accepts `--since` / `--until` as `YYYY-MM-DD`.

Sort: `relevance` (default; best for topical search), `submittedDate` (newest first when `--order descending`), `lastUpdatedDate`.

`id_list` is the right way to fetch by id, including versions (`1706.03762v1`). Do not use `search_query=id:...`.

### Mapping tips

- Multi-word titles and phrases: keep them as one quoted phrase (`ti:"attention is all you need"`), not a bag of `AND`s.
- Authors: start with the last name (`--author Vaswani`). Add a given name or quoted full name only if the first result set is too broad. Underscores also work (`au:del_maestro`).
- Categories: one `--cat cs.LG` is a filter. Several `--cat` flags are OR'd. Combining category with keywords uses AND.
- "Recent papers on X": `--sort submittedDate --max 8` and a tight `--cat`, not a huge `all:` dump.
- Noisy keyword hits (the term appears once in an unrelated abstract): retry with `--field abs` or `--title`, or add a quoted phrase in `--raw`.
- Both `search_query` and `id_list`: API returns only those ids that also match the query (a filter). The script does not mix them; pick one command.

## Present results

Lead with a one-line tally: `N shown of total_results`, plus the `search_query` or ids you used.

For each paper:

```
**{title}**
{authors, comma-separated} · arXiv:{id}{version} · {primary_category} · {published date}
{two-sentence abstract — trim the summary, do not rewrite claims}
[abs]({abs_url}) · [pdf]({pdf_url})
```

Include `journal_ref` or `doi` when present. If `total_results` is huge, say so and offer a tighter `--cat`, quoted phrase, or date range rather than paging blindly.

Zero hits: show the exact `search_query`, then retry once with a looser field (`all:` instead of `ti:`) or fewer ANDs. Still empty? Stop and say so.

## Follow-ups

- Summarize or compare only from returned metadata unless the user asks to read a PDF.
- Fetch a PDF only for papers the user named. Link to the abstract page (`abs_url`) as the canonical citation.
- Next page: same query with `--start` incremented by `--max`. Wait at least 3 seconds between API calls.
- Bulk harvest (thousands of records) is out of scope; point at [OAI-PMH](https://info.arxiv.org/help/oa/index.html) instead.

## Constraints

These exist so arXiv stays up for everyone.

- One request at a time. At most one call every 3 seconds. The script retries once on 429/5xx and falls back to `curl` (or HTTP) if Python's TLS store is missing certificates. Do not hammer the endpoint yourself.
- Keep `--max` small (8 is the default; 25 is plenty for a chat). The script caps at 100.
- Same query does not change until the next daily announcement cycle. Do not poll.
- Metadata is CC0. Paper PDFs and source are copyrighted; do not scrape and re-host them.
- Official docs: [API user manual](https://info.arxiv.org/help/api/user-manual.html), [API terms](https://info.arxiv.org/help/api/tou.html), [identifiers](https://info.arxiv.org/help/arxiv_identifier.html).
