# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo actually is right now

`knowledgebase-cli` is an AgentCulture mesh agent **scaffolded from
`culture-agent-template`** (see `git log`). Its *stated* domain — "manages
Amazon Bedrock Knowledge Bases (data sources, ingestion jobs, managed-RAG
retrieval)" — is the **intended** purpose and is **not yet implemented**. There
is no Bedrock / `boto3` code anywhere; runtime `dependencies = []`.

What exists today is the generic **agent-first CLI** surface inherited from the
template: the verbs `whoami`, `learn`, `explain`, `overview`, `doctor`, and the
`cli` noun group. Their prose still self-describes the tool as "a clonable
template for AgentCulture mesh agents" (in `kb/cli/_commands/learn.py`,
`kb/explain/catalog.py`, `kb/cli/_commands/overview.py`). When you implement the
Bedrock domain, that self-describing prose needs rewriting too — it is residue,
not the real description.

So the real near-term work is: **add Bedrock KB noun groups** (e.g.
`datasource`, `ingestion`, `retrieve`) following the extension pattern below,
and rebrand the template prose. Do not invent Bedrock behavior that isn't there.

## Naming — three different names for one thing

These differ and the difference bites:

- **`knowledgebase-cli`** — the PyPI/dist name, the argparse `prog` string, and
  the **primary console script** (`[project.scripts]`). This is the canonical
  command; all `--help`/usage/output self-identifies as `knowledgebase-cli`.
- **`kb`** — the import package (`kb/`) **and** a **short-alias** console script
  that dispatches the same entry point (parallel to colleague's `colleague` /
  `clg`). `kb …` and `knowledgebase-cli …` are interchangeable.
- So `uv run knowledgebase-cli whoami` and `uv run kb whoami` both work. The
  import package name (`kb`) deliberately stays short; only it differs from the
  agent name, and it's internal (never user-facing).

## Commands

```bash
uv sync                                  # create .venv, install runtime + dev deps
uv run kb whoami                         # smallest identity probe (reads culture.yaml)
uv run kb learn --json                   # self-teaching prompt (every verb takes --json)

uv run pytest -n auto                    # full suite (parallel via xdist)
uv run pytest tests/test_cli.py::test_whoami_text   # a single test
uv run pytest -n auto --cov=kb --cov-report=term    # with coverage (CI gate: fail_under=60)

# Lint — all four must pass (the `lint` CI job runs exactly these):
uv run black --check kb tests
uv run isort --check-only kb tests
uv run flake8 kb tests
uv run bandit -c pyproject.toml -r kb
markdownlint-cli2 "**/*.md" "#node_modules" "#.local" "#.claude/skills" "#.teken"

uv run teken cli doctor . --strict       # the agent-first rubric gate CI enforces
```

`teken>=0.8` is a **dev dependency only** — it provides the rubric checker
(`teken cli doctor`); the runtime ships zero third-party deps and must stay that
way (the CLI was *cited*, not imported, from teken's `afi-cli` `python-cli`
reference). Don't add it to `[project] dependencies`.

## Architecture

### CLI dispatch (`kb/cli/__init__.py`)

`main(argv)` → `_build_parser()` builds the top-level parser and calls each
command module's `register(sub)` → `parse_args` → `_dispatch(args)` invokes
`args.func(args)`. To add a verb/noun, write a module under
`kb/cli/_commands/` exposing `register(sub)`, then add one `register()` call in
`_build_parser()` (there is a marked "Register your own noun groups here" spot).
That is the entire extension surface — this is where Bedrock noun groups go.

### Two stable contracts (do not break these — the rubric and tests enforce them)

1. **Error / exit-code contract** (`kb/cli/_errors.py`): every failure raises
   `CliError(code, message, remediation)`. `_dispatch` catches it, routes
   through `emit_error`, and returns `code`. Any *other* exception is wrapped
   into a `CliError` so **no Python traceback ever leaks to stderr**. Exit
   codes: `0` success, `1` user-input error, `2` environment/setup error, `3+`
   reserved. Argparse-level errors (unknown verb, bad flag) are *also* funneled
   through this contract via `_CliArgumentParser.error()` — and they exit `1`,
   not argparse's default `2`. Because parse errors fire before `args.json`
   exists, `main()` pre-scans raw argv for `--json` and stashes it on the
   class-level `_CliArgumentParser._json_hint`; `parser_class=_CliArgumentParser`
   propagates the override to every subparser (so nested `cli overview --bogus`
   honors it too).

2. **Output contract** (`kb/cli/_output.py`): **results → stdout, errors and
   diagnostics → stderr, never mixed.** Every command supports `--json`. In text
   mode an error renders as `error: <msg>` then `hint: <remediation>` — the
   `hint:` prefix is **required by the agent-first rubric**, so keep it. Always
   emit through `emit_result` / `emit_error` / `emit_diagnostic`; don't `print`.

### Explain catalog (`kb/explain/`)

`explain` is a *global* verb (not nested under a noun). `kb/explain/catalog.py`
maps command-path tuples → verbatim markdown (`()` and `("knowledgebase-cli",)`
both resolve to root). `resolve()` raises `CliError` on an unknown path.
`tests/test_cli.py::test_every_catalog_path_resolves` asserts every registered
path resolves — **when you add a verb, add a matching catalog entry** or that
test fails.

### Identity introspection

`whoami`/`doctor`/`overview` read identity by parsing `culture.yaml` *without a
YAML dependency* (`read_agent_fields` in `whoami.py` does hand-rolled
`key: value` scanning of the first agent block). `find_culture_yaml()` walks up
from `__file__`, so identity is always the agent's own — in a wheel install
where no `culture.yaml` ships, it falls back to literal defaults and `doctor`
reports a single info check and exits 0.

## Mesh identity — and why `AGENTS.colleague.md`, not this file, is the runtime prompt

`culture.yaml` declares the agent. It was **promoted from `backend: claude` to
`backend: colleague`** (CHANGELOG 0.3.0) with a pinned model. The
backend→prompt-file map (in `kb/cli/_commands/doctor.py`) is:

| backend | runtime prompt file |
|---------|---------------------|
| `claude` | `CLAUDE.md` |
| `colleague` | `AGENTS.colleague.md` |
| `acp` | `AGENTS.md` |
| `gemini` | `GEMINI.md` |

So the **mesh runtime prompt for this agent is `AGENTS.colleague.md`** — that is
the file the colleague backend loads when the agent runs in the mesh (the
colleague runtime composes `AGENTS.md` → `AGENTS.colleague.md` →
`AGENTS.colleague.<model>.md`, and folds `.claude/skills/*/SKILL.md` in via
`colleague learn_from`). **This `CLAUDE.md` is the Claude Code *developer*
guidance file**, not the runtime prompt. `knowledgebase-cli doctor` checks that
`AGENTS.colleague.md` is present and passes.

The `doctor` map keeps all four backends so the check is reusable, but **this
agent is `colleague`** — keep `culture.yaml`, the README, the explain catalog,
and `docs/skill-sources.md` consistent with that (a past promotion left
`backend: claude` text scattered around; it has been reconciled — don't
reintroduce it).

## Vendored skills — cite-don't-import

`.claude/skills/` holds 11 skills vendored verbatim from **guildmaster** (the
AgentCulture skills supplier), with provenance tracked in
`docs/skill-sources.md`. Rules:

- **Never reformat or hand-edit script bodies** under `.claude/skills/**` — they
  are cited copies. `markdownlint`, Sonar, and black all *exclude* that tree.
- Only `SKILL.md` files carry identifier-only adaptations (consumer name, an
  added `type: command` line — load-bearing: `core.skill_loader` silently skips
  any `SKILL.md` without `type:`). To update a skill, re-sync from upstream per
  the procedure in `docs/skill-sources.md`, then re-apply only those adaptations.
- Two tracked divergences from "cite guildmaster's copy" exist: `agex`→`devex`
  (patched in place) and `outsource`→`ask-colleague` (vendored straight from the
  sibling `colleague` checkout). Don't "fix" them without reading
  `docs/skill-sources.md`.

## Git workflow

Branch → implement → **bump the version** → PR → address review → merge. The
`version-check` CI job (PR-only) fails the build if `pyproject.toml`'s version
equals `main`'s — **every PR bumps the version, even docs/config/CI-only ones.**
Use the `version-bump` skill (`/version-bump patch|minor|major`), which also
prepends a Keep-a-Changelog entry to `CHANGELOG.md`. Use the `cicd` skill for
the PR lifecycle (open/read/reply/status/await — it gates on the SonarCloud
quality gate and unresolved review threads).

## CI / publish

- **`.github/workflows/tests.yml`** — three jobs: `test` (pytest + coverage,
  then a SonarCloud scan *only when `SONAR_TOKEN` is set*, so fork PRs and
  token-less repos stay green; the gate blocks via `sonar.qualitygate.wait`),
  `lint` (the five lint commands above + the `teken` rubric gate), and
  `version-check`.
- **`.github/workflows/publish.yml`** — PyPI Trusted Publishing (OIDC, no
  tokens). PRs touching `pyproject.toml`/`kb/**` publish a `.devN` build to
  TestPyPI; push to `main` publishes to PyPI.
- **Coverage→Sonar mapping** depends on `[tool.coverage.run] relative_files =
  true` in `pyproject.toml` (emits repo-relative paths that map to
  `sonar.sources=kb`). Don't remove it — absolute/`.venv` paths get dropped as
  unmappable and coverage silently reads 0%.

## Rebranding the residual template prose

The scaffold name appears in ~85 lines across `kb/`, `tests/`, `pyproject.toml`,
`sonar-project.properties`, and `README.md`. To find every occurrence before a
rename or a domain rewrite:

```bash
git grep -n -I "knowledgebase-cli"
```

## Conventions and workflow

**Memory discipline — recall before, remember after.** This repo keeps its
eidetic memory **in-repo and public**: records resolve to
`<repo-root>/.eidetic/memory` — committed, and shared with the team and mesh
peers (the `claude` and `colleague` backends both read the same
`knowledgebase-cli` scope), so memory travels with the repo, not a private
home-dir store. Make it a per-task habit:

- **`/recall` before you start.** Search the store for the area you're about
  to touch — prior decisions, gotchas, "have we done this before?" — so you
  build on what's already known instead of re-deriving it. Do this before
  non-trivial tasks, not just when asked.
- **`/remember` when something worth keeping surfaces.** A non-obvious
  decision and its rationale, a constraint, a fix and *why* it was needed, a
  gotcha that cost time, a fact the next session would otherwise re-learn.
  Capture it as it happens, not at the end when it's faded.

A plain `/remember` lands the note in `./.eidetic/memory` in this repo — no
flag needed (the wrappers here default to `--visibility public`; in-repo
routing needs `eidetic >= 0.10.0`, older CLIs keep records in `$HOME`). Keep
something out of the committed store only by passing `--visibility private`
(routes to `$HOME/.eidetic/memory`, never committed); `/recall` reads both
stores and merges. Don't store what the repo already records (code structure,
git history, what's already in this file or `CHANGELOG.md`) — store what you'd
have to re-derive. These are the `recall`/`remember` skills (`.claude/skills/`),
backed by the `eidetic` store.
