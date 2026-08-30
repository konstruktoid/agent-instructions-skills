#!/usr/bin/env python3
"""Check that the line citations in this repository's prose still resolve.

`docs/threat-model.md`, `docs/controls.md` and `README.md` argue from citations of the form
`path/to/file.md:123`. An edit above a cited line moves it silently, and nothing in the
repository read a citation until this script.

Every citation naming both a path and a line is held to four things: a line number within the
file; a cited line that is not blank, since a blank line is what a shifted number usually lands
on; a range that runs forwards, since a backwards one is a half-applied renumbering; and, where
the citing sentence quotes the source, the quoted text near the cited line. The quote is the
only part of a citation that says what was meant, so it is the only part that catches one which
drifted onto a different line that happens to hold something.

A cited path resolves as a repository path, or as a unique path suffix among tracked files,
because the documents abbreviate. Eval fixtures and results are left out of that index, since a
fixture ships its own `lint.yml` and would make every citation of the real one ambiguous.

Three things go unchecked, which is most of them. A bare continuation, `` `:21` `` after a path
named earlier, belongs to whichever file the sentence last named, which is a question about
English; only its ordering within a range is checked. A path suffix matching more than one
tracked file, such as a bare `SKILL.md`, names no single target. And a citation pointing at the
wrong non-blank line with no quote beside it carries nothing that says where it was meant to
point. The first two are counted in the summary rather than passed over in silence.

Run it from anywhere; it reports on the checkout it lives in and needs only the standard
library:

    python3 scripts/check_citations.py

Exits 0 when every checked citation holds, 1 otherwise.
"""

from __future__ import annotations

import io
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

GIT = shutil.which("git") or "git"

REPO_ROOT = Path(__file__).resolve().parent.parent

CITING_GLOBS = (
    "README.md",
    "SECURITY.md",
    "docs/*.md",
    "instructions/*.md",
    "skills/**/*.md",
    "agent-templates/*.md",
    "evals/README.md",
    "evals/*/README.md",
)

# A fixture is a planted copy of a real file, so indexing one makes real citations ambiguous.
NOT_A_TARGET = re.compile(r"^evals/[^/]+/(?:fixtures|results)/")

# The lookbehind excludes a longer path's tail; the extension excludes versions and digests.
CITATION = re.compile(r"(?<![\w/-])([\w.-]+(?:/[\w.-]+)*\.[a-z]{2,5}):(\d+)\b")

# Not checked, but it ends the quote search: a following quote belongs to it, not to this.
BARE_CITATION = re.compile(r"`:\d+`")

# A range end or further line extends the citation before it, so a following quote covers all.
CONTINUATION = re.compile(r"^`?(?:\s*[-,]\s*`:\d+`)+\s*")

# A backwards or single-line range is what a half-applied renumbering leaves behind.
RANGE_END = re.compile(r"^`?-`:(\d+)`")

# The minimum length ignores quoted single words, which are terms rather than cited passages.
QUOTED = re.compile(r'"([^"]{24,})"')
QUOTE_LOOKAHEAD = 400
QUOTE_MUST_START_WITHIN = 120

# A citation names where a passage starts, and a wrapped passage runs past it.
WINDOW_BEFORE = 2
WINDOW_AFTER = 8


def collapse(text: str) -> str:
    """Return one line of text with every run of whitespace reduced to a single space."""
    return re.sub(r"\s+", " ", text).strip()


def tracked_files() -> list[str]:
    """Return the repository-relative path of every tracked file outside eval fixtures."""
    # Fixed argument list, no shell.
    result = subprocess.run(  # noqa: S603
        [GIT, "ls-files"], cwd=REPO_ROOT, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        return []
    return [path for path in result.stdout.split() if not NOT_A_TARGET.match(path)]


def candidates(cited: str, tracked: list[str]) -> list[str]:
    """Return the tracked files a cited path could name, in repository-relative form.

    A citation is checked only when this returns exactly one, which keeps "names nothing" and
    "names several" the same answer: a citation this cannot check.
    """
    if (REPO_ROOT / cited).is_file():
        return [cited]
    return [path for path in tracked if path == cited or path.endswith(f"/{cited}")]


def quote_after(text: str, offset: int) -> str | None:
    """Return the quoted passage a citation is followed by, None when it carries none.

    The search stops at the next citation of either form, so a following citation's quote is
    not read as evidence for this one.
    """
    window = collapse(text[offset : offset + QUOTE_LOOKAHEAD])
    window = CONTINUATION.sub("", window)
    quoted = QUOTED.search(window)
    if quoted is None or quoted.start() > QUOTE_MUST_START_WITHIN:
        return None
    preceding = window[: quoted.start()]
    if CITATION.search(preceding) or BARE_CITATION.search(preceding):
        return None
    return collapse(quoted.group(1)).rstrip(".")


def check_citation(cited: str, number: int, target: Path) -> str | None:
    """Return the failure one resolved citation carries, None when it holds."""
    lines = target.read_text(encoding="utf-8").splitlines()
    if not 1 <= number <= len(lines):
        return f"{cited}:{number} is past the end of the file, which has {len(lines)} lines"
    if not lines[number - 1].strip():
        return f"{cited}:{number} lands on a blank line"
    return None


def check_quote(cited: str, number: int, target: Path, quote: str) -> str | None:
    """Return the failure a quoted citation carries, None when the quote is where it says."""
    lines = target.read_text(encoding="utf-8").splitlines()
    start = max(0, number - 1 - WINDOW_BEFORE)
    body = collapse(" ".join(lines[start : number + WINDOW_AFTER]))
    if quote.lower() in body.lower():
        return None
    return f'{cited}:{number} does not carry the text quoted beside it: "{quote[:72]}"'


def check_document(doc: Path, tracked: list[str]) -> tuple[list[str], Counter[str]]:
    """Return one document's failures and a tally of what was checked in it."""
    failures: list[str] = []
    tally: Counter[str] = Counter()
    text = doc.read_text(encoding="utf-8")

    for match in CITATION.finditer(text):
        cited, number = match.group(1), int(match.group(2))
        line = text.count("\n", 0, match.start()) + 1

        # Checked before resolution, since it holds whatever file the range names.
        end = RANGE_END.match(text[match.end() :])
        if end is not None and int(end.group(1)) <= number:
            tally["ranges"] += 1
            failures.append(
                f"{doc.relative_to(REPO_ROOT)}:{line}: {cited}:{number} opens a range ending at "
                f":{end.group(1)}, which is not after it"
            )

        matches = candidates(cited, tracked)
        if len(matches) != 1:
            tally["skipped"] += 1
            continue
        target = REPO_ROOT / matches[0]
        failure = check_citation(cited, number, target)
        if failure is None:
            tally["checked"] += 1
            quote = quote_after(text, match.end())
            if quote is not None:
                tally["quoted"] += 1
                failure = check_quote(cited, number, target, quote)
        if failure is not None:
            failures.append(f"{doc.relative_to(REPO_ROOT)}:{line}: {failure}")

    return failures, tally


def main() -> int:
    """Check every citation in this repository's prose and report the ones that do not hold."""
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(line_buffering=True)

    tracked = tracked_files()
    if not tracked:
        print("no tracked files found; nothing to resolve citations against", file=sys.stderr)
        return 1

    docs = sorted({path for glob in CITING_GLOBS for path in REPO_ROOT.glob(glob)})
    failures: list[str] = []
    counts: Counter[str] = Counter()
    for doc in docs:
        doc_failures, doc_tally = check_document(doc, tracked)
        failures += doc_failures
        counts += doc_tally

    for failure in failures:
        print(failure, file=sys.stderr)

    tally = (
        f"{counts['checked']} citation(s) across {len(docs)} document(s) resolve to one file "
        f"and name a line that exists and is not blank; {counts['quoted']} of those also carry "
        f"the text quoted beside them; {counts['skipped']} resolve to no single file, unchecked"
    )
    if failures:
        print(f"\n{len(failures)} citation(s) do not hold; {tally}", file=sys.stderr)
        return 1

    print(f"citations: {tally}.")
    print("a citation with no quote beside it is held only to naming a non-blank line in range")
    return 0


if __name__ == "__main__":
    sys.exit(main())
