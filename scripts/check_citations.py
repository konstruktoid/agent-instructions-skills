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

An edit that moves a cited line is mechanical to repair, so `--renumber` repairs it: it reads
the working tree against `HEAD`, maps every cited target's old line numbers to its new ones, and
rewrites the citations that moved. It refuses to run while a citing document has uncommitted
changes of its own, since the mapping runs from `HEAD` and a number already corrected by hand
reads the same as one that never moved, so rewriting it would shift it twice.

Run it from anywhere; it reports on the checkout it lives in and needs only the standard
library:

    python3 scripts/check_citations.py
    python3 scripts/check_citations.py --renumber

Exits 0 when every checked citation holds, 1 otherwise.
"""

from __future__ import annotations

import argparse
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

# `git diff -U0` emits only headers and changed lines, so the headers alone carry the mapping.
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


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
    # A cited path is prose, so it can climb out of the checkout or through a symlink; one that
    # lands outside names nothing this repository can argue from.
    direct = (REPO_ROOT / cited).resolve()
    if direct.is_file() and direct.is_relative_to(REPO_ROOT):
        return [direct.relative_to(REPO_ROOT).as_posix()]
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


def check_range_end(cited: str, number: int, end: int, target: Path) -> str | None:
    """Return the failure a range's endpoint carries, None when the file reaches that far."""
    lines = target.read_text(encoding="utf-8").splitlines()
    if end > len(lines):
        return (
            f"{cited}:{number} opens a range ending at :{end}, past the end of the file, "
            f"which has {len(lines)} lines"
        )
    return None


def locate_quote(lines: list[str], quote: str) -> int | None:
    """Return the line a quoted passage starts on, None when the file holds it zero or twice.

    Blank lines are dropped and the rest joined by a single space, which is what `check_quote`
    compares against, so a passage found here would satisfy the citation that named its line.
    """
    starts: list[tuple[int, int]] = []
    parts: list[str] = []
    position = 0
    for number, line in enumerate(lines, start=1):
        collapsed = collapse(line)
        if not collapsed:
            continue
        if parts:
            position += 1
        starts.append((position, number))
        parts.append(collapsed)
        position += len(collapsed)

    body = " ".join(parts).lower()
    needle = quote.lower()
    first = body.find(needle)
    if first < 0 or body.find(needle, first + 1) >= 0:
        return None
    return max(number for offset, number in starts if offset <= first)


def check_quote(cited: str, number: int, target: Path, quote: str) -> str | None:
    """Return the failure a quoted citation carries, None when the quote is where it says."""
    lines = target.read_text(encoding="utf-8").splitlines()
    start = max(0, number - 1 - WINDOW_BEFORE)
    body = collapse(" ".join(lines[start : number + WINDOW_AFTER]))
    if quote.lower() in body.lower():
        return None
    # The window is what the citation claims; naming where the passage actually sits turns the
    # failure into the correction, which is the only part of a citation a reader cannot derive.
    moved = locate_quote(lines, quote)
    if moved is not None:
        return (
            f"{cited}:{number} names the wrong line for the text quoted beside it, "
            f"which is at :{moved}"
        )
    return f'{cited}:{number} does not carry the text quoted beside it: "{quote[:72]}"'


def line_map(target: str) -> dict[int, int] | None:
    """Return each line of a target at `HEAD` mapped to its line now, None when it is unchanged.

    A line inside a hunk's replaced range is left out rather than guessed at: its content is not
    the content the citation was written against, so no number for it is defensible.
    """
    # Fixed argument list, no shell.
    result = subprocess.run(  # noqa: S603
        [GIT, "diff", "-U0", "HEAD", "--", target],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return None

    hunks: list[tuple[int, int, int]] = []
    for line in result.stdout.splitlines():
        header = HUNK.match(line)
        if header is None:
            continue
        old_start, old_count, new_count = (
            int(header.group(1)),
            int(header.group(2) or 1),
            int(header.group(4) or 1),
        )
        hunks.append((old_start, old_count, new_count - old_count))

    new_lines = len((REPO_ROOT / target).read_text(encoding="utf-8").splitlines())
    # The mapping runs over the old file, whose length is the new one's less what the hunks added.
    old_lines = new_lines - sum(shift for _, _, shift in hunks)
    reach = max([old_lines] + [start + count for start, count, _ in hunks])
    moved = (moved_line(number, hunks) for number in range(1, reach + 1))
    return {number: new for number, new in enumerate(moved, start=1) if new is not None}


def moved_line(number: int, hunks: list[tuple[int, int, int]]) -> int | None:
    """Return where one line of the old file sits now, None when a hunk replaced it."""
    delta = 0
    for old_start, old_count, shift in hunks:
        # A pure insertion carries `old_count` 0 and sits after `old_start`, so it moves the
        # lines below that one without replacing any.
        if old_count == 0:
            if number > old_start:
                delta += shift
        elif number >= old_start + old_count:
            delta += shift
        elif number >= old_start:
            return None
    return number + delta


def modified_documents(docs: list[Path]) -> list[str]:
    """Return the citing documents renumbering cannot trust, modified or untracked.

    The mapping runs from `HEAD`, so a document written against the working tree already
    holds the numbers the mapping would move it to, and rewriting it shifts them twice. An
    untracked document was written that way by definition, and git holds no copy of it to
    restore from afterwards.
    """
    paths = [str(doc) for doc in docs]
    changed: set[str] = set()
    for arguments in (
        ["diff", "--name-only", "HEAD", "--", *paths],
        ["ls-files", "--others", "--exclude-standard", "--", *paths],
    ):
        # Fixed argument list, no shell.
        result = subprocess.run(  # noqa: S603
            [GIT, *arguments], cwd=REPO_ROOT, capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            changed.update(path for path in result.stdout.split() if path)
    return sorted(changed)


def renumber_document(doc: Path, maps: dict[str, dict[int, int]], tracked: list[str]) -> list[str]:
    """Rewrite one document's moved citations in place, returning a line for each one moved."""
    text = doc.read_text(encoding="utf-8")
    moved: list[str] = []
    pieces: list[str] = []
    cursor = 0

    for match in CITATION.finditer(text):
        cited, number = match.group(1), int(match.group(2))
        matches = candidates(cited, tracked)
        if len(matches) != 1:
            continue
        mapping = maps.get(matches[0])
        if mapping is None:
            continue

        end = RANGE_END.match(text[match.end() :])
        tail = end.group(0) if end is not None else ""
        span_end = match.end() + (end.end() if end is not None else 0)

        citation = f"{cited}:{mapping.get(number, number)}"
        if end is not None:
            end_line = int(end.group(1))
            tail = tail.replace(f":{end_line}`", f":{mapping.get(end_line, end_line)}`", 1)
        if citation + tail == text[match.start() : span_end]:
            continue

        line = text.count("\n", 0, match.start()) + 1
        moved.append(
            f"{doc.relative_to(REPO_ROOT)}:{line}: "
            f"{text[match.start() : span_end]} -> {citation}{tail}"
        )
        pieces.append(text[cursor : match.start()])
        pieces.append(citation + tail)
        cursor = span_end

    if moved:
        pieces.append(text[cursor:])
        doc.write_text("".join(pieces), encoding="utf-8")
    return moved


def renumber(docs: list[Path], tracked: list[str]) -> int:
    """Rewrite every citation whose target moved since `HEAD`, and report what was rewritten."""
    dirty = modified_documents(docs)
    if dirty:
        # The mapping runs from `HEAD`, so a citation already corrected by hand is indistinguishable
        # from one that never moved, and rewriting it shifts it a second time.
        print(
            "renumber: these citing document(s) are modified or untracked, so a citation in "
            "them may already have been corrected by hand and would be shifted twice:",
            file=sys.stderr,
        )
        for doc in dirty:
            print(f"  {doc}", file=sys.stderr)
        print("commit them, or correct the remaining citations by hand", file=sys.stderr)
        return 1

    cited_paths = set()
    for doc in docs:
        text = doc.read_text(encoding="utf-8")
        for match in CITATION.finditer(text):
            matches = candidates(match.group(1), tracked)
            if len(matches) == 1:
                cited_paths.add(matches[0])

    maps = {path: line_map(path) for path in sorted(cited_paths)}
    maps = {path: mapping for path, mapping in maps.items() if mapping is not None}
    if not maps:
        print("renumber: no cited file has changed since HEAD, so no citation has moved")
        return 0

    moved: list[str] = []
    for doc in docs:
        moved += renumber_document(doc, maps, tracked)
    for line in moved:
        print(line)
    print(
        f"renumber: {len(moved)} citation(s) rewritten across {len(maps)} changed file(s); "
        "re-run without --renumber to check them"
    )
    return 0


def check_document(doc: Path, tracked: list[str]) -> tuple[list[str], Counter[str]]:
    """Return one document's failures and a tally of what was checked in it."""
    failures: list[str] = []
    tally: Counter[str] = Counter()
    text = doc.read_text(encoding="utf-8")

    for match in CITATION.finditer(text):
        cited, number = match.group(1), int(match.group(2))
        line = text.count("\n", 0, match.start()) + 1

        # Ordering holds whatever file the range names, so it is checked before resolution.
        end = RANGE_END.match(text[match.end() :])
        end_line = int(end.group(1)) if end is not None else None
        if end_line is not None:
            tally["ranges"] += 1
        if end_line is not None and end_line <= number:
            failures.append(
                f"{doc.relative_to(REPO_ROOT)}:{line}: {cited}:{number} opens a range ending at "
                f":{end_line}, which is not after it"
            )
            end_line = None

        matches = candidates(cited, tracked)
        if len(matches) != 1:
            tally["skipped"] += 1
            continue
        target = REPO_ROOT / matches[0]
        failure = check_citation(cited, number, target)
        if failure is None and end_line is not None:
            failure = check_range_end(cited, number, end_line, target)
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
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--renumber",
        action="store_true",
        help="rewrite citations whose target moved since HEAD, instead of checking them",
    )
    args = parser.parse_args()

    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(line_buffering=True)

    tracked = tracked_files()
    if not tracked:
        print("no tracked files found; nothing to resolve citations against", file=sys.stderr)
        return 1

    docs = sorted({path for glob in CITING_GLOBS for path in REPO_ROOT.glob(glob)})
    if args.renumber:
        return renumber(docs, tracked)

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
