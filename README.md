# Agent Skills

A catalog of reusable agent skills. Each skill is a root-level folder with a `SKILL.md` that tells coding agents how to do one job well.

Coding agents should read [`AGENTS.md`](AGENTS.md) before creating or editing skills.

## Skills

| Skill | What it is for | Install |
| ----- | -------------- | ------- |
| [bootstrap-5](bootstrap-5/SKILL.md) | Bootstrap 5 UI: utility-first layout, grid, and components across HTML, Vue, React, and similar stacks | `npx skills add alen-hh/agent-skills@bootstrap-5` |
| [dankoe-style-writing](dankoe-style-writing/SKILL.md) | Essays, newsletters, and social posts in Dan Koe's style | `npx skills add alen-hh/agent-skills@dankoe-style-writing` |
| [dsh-plugin](dsh-plugin/SKILL.md) | DeepSeek Harness (dsh) plugins with Cordis: tools, services, LLM adapters, and bundles | `npx skills add alen-hh/agent-skills@dsh-plugin` |
| [oclif](oclif/SKILL.md) | Create and maintain CLIs with the oclif framework | `npx skills add alen-hh/agent-skills@oclif` |
| [reddit-marketing](reddit-marketing/SKILL.md) | Reddit marketing: communities, organic posts, AMAs, and ads | `npx skills add alen-hh/agent-skills@reddit-marketing` |

## Install

Use the [Skills CLI](https://skills.sh/) to install a skill into your coding agents:

```bash
npx skills add alen-hh/agent-skills@bootstrap-5
npx skills add alen-hh/agent-skills@dankoe-style-writing
npx skills add alen-hh/agent-skills@dsh-plugin
npx skills add alen-hh/agent-skills@oclif
npx skills add alen-hh/agent-skills@reddit-marketing
```

Install every skill in this repo:

```bash
npx skills add alen-hh/agent-skills --skill '*'
```

Add `-g` to install globally (user-level) instead of into the current project. Add `-y` to skip prompts.

## Layout

Every published skill lives at the **repository root**, next to this README:

```
agent-skills/
├── AGENTS.md
├── README.md
├── bootstrap-5/
├── dankoe-style-writing/
├── dsh-plugin/
├── oclif/
└── reddit-marketing/
```

A skill directory is named in kebab-case and contains at least `SKILL.md`. Optional extras: `references/` for long docs and `scripts/` for helpers. Do not commit `evals/` in this catalog.

Do not nest new skills under `skills/`, `.cursor/skills/`, or any other subdirectory.

To install from a local checkout instead of GitHub:

```bash
npx skills add ./bootstrap-5
```
