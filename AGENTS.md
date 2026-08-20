# AGENTS.md

This repository is a catalog of reusable agent skills. Coding agents work here to create, revise, evaluate, and catalog `SKILL.md` packages — not to build an application.

`README.md` is the human-facing skill index. This file is the source of truth for agents. Do not recreate project conventions in `.cursor/rules/`.

## Language And Communication

- Use **English** for all project-facing artifacts: source, identifiers, comments, commit messages, docs, tests, config, and skill files.
- Use **Chinese** when communicating directly with the developer in chat: explanations, progress updates, questions, and final responses.
- Preserve existing language when editing quoted text or third-party content.
- If the developer explicitly asks for another language, follow that request for that response.

## Required Authoring Skills

Do not invent a skill-authoring process from general knowledge. Before creating, editing, evaluating, packaging, or optimizing a skill, **read and follow** the relevant skill:

| Task | Skill to invoke first |
|------|------------------------|
| Create a new skill, iterate on an existing one, write evals, run benchmarks, or optimize a description | `skill-creator` |
| Cursor-specific `SKILL.md` format, storage locations, or authoring checklist | `create-skill` |
| Search whether a skill already exists before adding a duplicate | `find-skills` |
| Test-driven skill authoring (baseline without skill, then with skill) | `writing-skills` |
| Create or update this file | `create-agentsmd` |

`skills-lock.json` records the authoring toolchain this repo expects (`skill-creator`, plus related Smithery/ClawHub tools). Prefer those locked skills over ad-hoc alternatives.

If a listed skill is missing from the current runtime, install it (for example `npx skills add <package>`) or tell the developer which skill could not be loaded. Do not skip the workflow.

## Skill Placement (Required)

A finished skill **must** live at this repository's **root**, as a sibling of `README.md` and `AGENTS.md` — the same layout as the skills already in the catalog (`bootstrap-5/`, `dankoe-style-writing/`, `dsh-plugin/`, `oclif/`, `reddit-marketing/`).

```
agent-skills/
├── AGENTS.md
├── README.md
├── bootstrap-5/SKILL.md
├── dankoe-style-writing/SKILL.md
├── dsh-plugin/SKILL.md
├── oclif/SKILL.md
├── reddit-marketing/SKILL.md
└── <new-skill-name>/SKILL.md    # add new skills here, at the root
```

Hard rules:

- Path is always `/<skill-name>/SKILL.md` at the repo root. Directory name equals the `name` frontmatter field (kebab-case).
- Do **not** nest published skills under `skills/`, `packages/`, `.cursor/skills/`, `~/.cursor/skills/`, or any other subdirectory.
- Do **not** put this repo's skills in `~/.cursor/skills-cursor/` (Cursor internals).
- Authoring tools such as `skill-creator` stay in the agent's runtime install path. They are not catalog entries and must not be copied into this repo as if they were.
- A skill is not done until it exists at the root **and** `README.md` lists it with its `npx skills add alen-hh/agent-skills@<skill-name>` install command.

## Repository Layout

Each published skill is a **root-level directory** named after the skill. There is no `src/`, `package.json`, or app runtime.

```
<skill-name>/                 # must be at the repository root
├── SKILL.md                  # required
├── references/               # optional, loaded only when SKILL.md points to it
├── evals/
│   ├── evals.json            # task evals (prompts + expected outcomes)
│   └── trigger-eval.json     # description-trigger evals (optional)
├── examples.md               # optional
└── scripts/                  # optional deterministic helpers
```

Current catalog (keep `README.md` in sync when this set changes):

- `bootstrap-5` — Bootstrap 5 UI
- `dankoe-style-writing` — writing style
- `dsh-plugin` — DeepSeek Harness plugin development
- `oclif` — oclif CLI framework
- `reddit-marketing` — Reddit marketing

## Setup Commands

This repo has no install, build, or dev-server step. Clone it and edit skill directories.

Useful authoring commands (run against `skill-creator`'s scripts directory in the runtime that provides it, typically `~/.claude/skills/skill-creator`):

```bash
# Validate frontmatter and SKILL.md constraints
python3 ~/.claude/skills/skill-creator/scripts/quick_validate.py <skill-directory>

# Package a skill into a .skill zip (excludes evals/ and junk files)
python3 -m scripts.package_skill <skill-directory>
# (run from the skill-creator directory so `scripts` is importable)
```

Discover existing public skills before creating a new one:

```bash
npx skills find <query>
```

## Development Workflow

1. **Confirm intent.** Creating, editing, evaluating, or packaging? If the user is exploring whether a skill already exists, use `find-skills` first.
2. **Invoke `skill-creator`.** Read its `SKILL.md` and follow its loop: capture intent → draft `SKILL.md` → evals → review → iterate → optional description optimization → package.
3. **Place the skill at the repo root.** Write it to `<kebab-case-name>/SKILL.md` next to the existing skill folders. Directory name must equal the `name` frontmatter field. Never nest it.
4. **Progressive disclosure.** Keep `SKILL.md` under ~500 lines. Put long reference material in `references/` (or sibling files like `examples.md`) and link them from `SKILL.md`. Agents should read only the file needed for the current task.
5. **Update the catalog.** After adding or removing a skill, update `README.md`: the skills table, the install command list, and the layout tree. Every skill needs `npx skills add alen-hh/agent-skills@<skill-name>`.
6. **Do not commit secrets.** Skills must not include malware, exploit code, credentials, or content that would surprise a user given the description.

### New skill checklist

- [ ] `skill-creator` (and `create-skill` if Cursor format details matter) was actually read and followed
- [ ] Skill directory is at the **repository root** (same level as `bootstrap-5/`, not nested)
- [ ] `name` is kebab-case, ≤64 characters, matches the directory name
- [ ] `description` states **what** the skill does **and when** to trigger it (third person, no `<`/`>`, ≤1024 characters)
- [ ] Frontmatter keys are only from: `name`, `description`, `license`, `allowed-tools`, `metadata`, `compatibility`
- [ ] `SKILL.md` body is instruction-shaped (imperative), not an essay
- [ ] Heavy docs live in `references/` and are linked with "read this when…" guidance
- [ ] `README.md` lists the skill, including `npx skills add alen-hh/agent-skills@<skill-name>`
- [ ] `python3 …/quick_validate.py <skill-directory>` passes

## Testing Instructions

There is no repo-wide test runner. Testing is per-skill, via `skill-creator`.

- Task evals live at `<skill>/evals/evals.json`. Follow `skill-creator`'s schema (`skill_name`, `evals[]` with `id`, `prompt`, `expected_output`, `files`).
- Trigger evals (should / should-not fire) live at `<skill>/evals/trigger-eval.json`.
- Run evals through `skill-creator` (with-skill vs baseline subagents, grader, eval viewer). Do not invent a parallel harness.
- Eval workspaces belong **beside** the skill directory as `<skill-name>-workspace/`, not inside the skill folder. Do not commit workspace output unless the developer asks.
- `evals/` is excluded from packaged `.skill` files; keep evals in git as the skill's test suite.
- After changing a skill, add or update evals for the behavior you changed.

Validate a skill directory:

```bash
python3 ~/.claude/skills/skill-creator/scripts/quick_validate.py bootstrap-5
```

Replace `bootstrap-5` with the skill you edited. Fix reported frontmatter issues before considering the work done.

## Code Style

- Skill identifiers: `kebab-case`, directory name === `name`.
- Descriptions: third person; include trigger terms; say both what and when.
- Instructions: imperative ("Read X", "Use Y"). Prefer explaining *why* over stacked ALWAYS/NEVER rules.
- One concern per skill. Split unrelated domains into separate skills.
- Reference files stay one level deep from `SKILL.md`. For files over ~300 lines, include a table of contents.
- Default to bundled `scripts/` for repetitive mechanical work instead of making every future agent re-derive it.
- Do not use Windows-style paths in skill docs.
- Do not put time-sensitive "before date X" instructions in the main body; park legacy notes under an "Old patterns" section if needed.

## Pull Request Guidelines

- Title format: `feat: add <skill-name> skill` / `fix: …` / `docs: …` / `chore: …`
- Commit in English, conventional-commit style (this repo's history uses `feat`, `fix`, `docs`, `chore`).
- Before considering a skill change complete:
  - `quick_validate.py` on the touched skill directory
  - `README.md` catalog is accurate
  - evals added or updated when the skill's behavior changed
- Do not commit `.DS_Store`, eval workspaces, or packaged `.skill` binaries unless requested.

## Additional Notes

- Official skill format background: [agents.md](https://agents.md/) for this file; Anthropic / Cursor skill-authoring guidance lives inside `skill-creator` and `create-skill` — read those rather than paraphrasing from memory.
- If instructions conflict: the closest `AGENTS.md` wins; explicit user chat prompts override everything.
- This file is living documentation. Update it when the catalog layout or authoring toolchain changes.
