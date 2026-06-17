"""Markdown catalog for ``knowledgebase-cli explain <path>``.

Each entry is verbatim markdown. Keys are command-path tuples. The empty tuple
and ``("knowledgebase-cli",)`` both resolve to the root entry.

Keep bodies self-contained: an agent reading one entry should get enough
context without chaining reads.
"""

from __future__ import annotations

_ROOT = """\
# knowledgebase-cli

A clonable template for AgentCulture mesh agents. It carries an agent-first CLI
(cited from the teken `python-cli` reference), a mesh identity (`culture.yaml` +
`CLAUDE.md`), the canonical guildmaster skill kit under `.claude/skills/`, and a
buildable/deployable package baseline. Clone it, rename the package, edit
`culture.yaml`, and you have a new agent.

## Verbs

- `knowledgebase-cli whoami` — identity probe from `culture.yaml`.
- `knowledgebase-cli learn` — structured self-teaching prompt.
- `knowledgebase-cli explain <path>` — markdown docs for any noun/verb.
- `knowledgebase-cli overview` — descriptive snapshot of the agent.
- `knowledgebase-cli doctor` — check the agent-identity invariants.
- `knowledgebase-cli cli overview` — describe the CLI surface.

## Exit-code policy

- `0` success
- `1` user-input error
- `2` environment / setup error
- `3+` reserved

## See also

- `knowledgebase-cli explain whoami`
- `knowledgebase-cli explain doctor`
"""

_WHOAMI = """\
# knowledgebase-cli whoami

Reports the agent's identity from `culture.yaml`: nick (`suffix`), backend,
served model, and the package version. Read-only.

## Usage

    knowledgebase-cli whoami
    knowledgebase-cli whoami --json
"""

_LEARN = """\
# knowledgebase-cli learn

Prints a structured self-teaching prompt covering purpose, command map,
exit-code policy, `--json` support, and the `explain` pointer.

## Usage

    knowledgebase-cli learn
    knowledgebase-cli learn --json
"""

_EXPLAIN = """\
# knowledgebase-cli explain <path>

Prints markdown documentation for any noun/verb path. Unlike `--help` (terse,
positional), `explain` is global and addressable by path.

## Usage

    knowledgebase-cli explain knowledgebase-cli
    knowledgebase-cli explain whoami
    knowledgebase-cli explain --json <path>
"""

_OVERVIEW = """\
# knowledgebase-cli overview

Read-only descriptive snapshot of the agent: identity (from `culture.yaml`), the
verb surface, and the sibling-pattern artifacts the template carries. Accepts an
ignored `target` so a stray path never hard-fails.

## Usage

    knowledgebase-cli overview
    knowledgebase-cli overview --json
"""

_DOCTOR = """\
# knowledgebase-cli doctor

Checks the agent-identity invariants `steward doctor` verifies:
prompt-file-present and backend-consistency (`claude` → `CLAUDE.md`), plus a
skills-present check. Exits 1 when unhealthy.

## Usage

    knowledgebase-cli doctor
    knowledgebase-cli doctor --json
"""

_CLI = """\
# knowledgebase-cli cli

Noun group for CLI-surface introspection. `cli overview` describes the CLI
itself (distinct from the global `overview`, which describes the agent).

## Usage

    knowledgebase-cli cli overview
    knowledgebase-cli cli overview --json
"""


ENTRIES: dict[tuple[str, ...], str] = {
    (): _ROOT,
    ("knowledgebase-cli",): _ROOT,
    ("whoami",): _WHOAMI,
    ("learn",): _LEARN,
    ("explain",): _EXPLAIN,
    ("overview",): _OVERVIEW,
    ("doctor",): _DOCTOR,
    ("cli",): _CLI,
    ("cli", "overview"): _CLI,
}
