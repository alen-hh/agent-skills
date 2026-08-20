---
name: dsh-plugin
description: Guide agents to develop DeepSeek Harness (dsh) plugins correctly with Cordis. Use whenever the user mentions DeepSeek Harness, dsh, dsh-plugin, cordis.yml, writing a Harness tool/service/LLM adapter, packaging a dsh.bundle, or installing with `dsh plugin` — even if they never say "plugin".
---

# DeepSeek Harness Plugin Development

A Harness plugin is a TypeScript module the Cordis loader mounts into a shared `Context`. Capabilities (tools, LLM adapters, services, listeners) are registered on `ctx` and unwind automatically when the plugin unloads.

Read only the reference file for the current task. Do not load all three at once.

| Task | Read |
|------|------|
| First plugin, local `--patch`, tools, config, packaging | [references/basic.md](references/basic.md) |
| Lifecycle, providing/consuming services, events | [references/framework.md](references/framework.md) |
| Replaceable three-role capabilities, new LLM providers | [references/practice.md](references/practice.md) |

Official source of truth: [docs/user/develop](https://github.com/deepseek-ai/deepseek-harness/tree/master/docs/user/develop). Prefer the live docs over memory when a type, event name, or CLI flag is in doubt.

## Mental model

1. **A plugin exports `apply(ctx)`.** Function form is enough for most work. Use a `Service` subclass only when this plugin *provides* a named capability other plugins `inject`.
2. **`inject` is the load-order contract.** Cordis waits until every required service exists before calling `apply`. Do not guess boot order.
3. **Registrations are reversible effects.** `ctx.on`, `ctx.tools.register`, `ctx.llm.registerAdapter`, and `ctx.effect` are cleaned up on unload. That is why HMR works.
4. **A bundle is what you ship.** `dsh.bundle` points at a patch layer. A profile is what a user boots; authors do not write profile manifests by hand.
5. **Later layers win per row.** A patch replaces a row's entire `config` by `id`. It does not deep-merge keys.

## Choose a shape

- **Local scratch plugin** (`--patch` overlay, absolute module path): iterate inside a Harness checkout. Start here for tutorials and one-off experiments.
- **Installable bundle** (`package.json` + `cordis.patch.yml` + `dsh plugin add`): anything another person or another profile should enable.
- **Library package** (no `dsh.bundle`): code that plugin packages import. `dsh plugin` will warn and activate no layer — that is correct.

Do not split a simple tool into Service Definition / Provider / Consumer packages. Three-role layering exists so a capability can have *replaceable providers*. A greet tool does not need it.

## Hard rules

These catch the mistakes agents make when they invent a plugin from general TypeScript habits.

**Loading and paths.** A `--patch` overlay does not change the profile directory the loader resolves from. Local plugin `name` values must be **absolute paths**. After packaging, patch rows reference the package name so Node resolution finds the installed code.

**Configuration.** Export a TypeScript `Config` interface *and* a same-named Schemastery `Schema`. Cordis validates against the Standard Schema interface; a plain object export is not a schema and will not fill defaults. Anything two deployments may want to set differently belongs in `Config` — hardcoded timeouts and URLs fail that test. Invalid config must fail at load, not at first request.

**Cleanup.** Custom resources (sockets, intervals, child processes) return a disposer from `ctx.effect()`. Async disposers may run concurrently; if teardown order matters, put the serial `await`s in **one** effect.

**Events.** Waterfall listeners **must call `next()`** to delegate; omitting it short-circuits on purpose. Cordis events use `namespace/action` names (`agent/step`, `tools/result`, `session/event`). Durable session types (`turn/*`, `step/*`, `tool/call`, `tool/result`, `compaction/*`) are not same-named Cordis events — listen to `session/event` and inspect `event.type`.

**Shipping.** A package without `dsh.bundle` installs as a plain dependency. Git installs fetch source, not `lib/`: ship a self-contained `prepare` script, and the user must allow the build under pnpm ≥10. Prefer publishing built artifacts (npm or `pnpm pack`) when you do not want that allowance.

**LLM adapters.** Throw `LlmError` with a stable code. Forward `options.signal`. Merge `attributionHeaders()` into every provider HTTP request. Every `block-start` needs a matching `block-end`. Emit `usage` before `finish`. `finish` is the last chunk.

## Workflow

1. Classify the task using the table above and read that reference.
2. Match the user's environment: Harness checkout + `pnpm dsh …`, or an installed `dsh` CLI + a named `--profile`.
3. Write the smallest plugin that satisfies the contract (`name`, `inject` if needed, `apply`, schema if configurable).
4. Load it: `--patch` for scratch work, `dsh plugin add` once it is a bundle.
5. Verify with `dsh --profile <name> --dump-config` before booting, then boot. Confirm the layer appears and the plugin actually registers (log, tool call, or adapter route).
6. Fetch official docs or generated subsystem pages only when the task needs a signature this skill does not include (nested tool schemas, a specific `ctx.*` method, cookbook UI cards).

## Official docs (fetch when needed)

- Basic path: [first plugin](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/index.md), [tool](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/tool.md), [config](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/config.md), [publish](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/basic/publish.md)
- Framework: [lifecycle](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/framework/index.md), [services](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/framework/service.md), [events](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/framework/events.md)
- Practice: [three-role](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/practice/index.md), [LLM adapter](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/user/develop/practice/llm-adapter.md)
- Deeper, not required for a first plugin: [Cordis primer](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cordis-primer.md), [Cordis tutorial](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cordis-tutorial/index.md), [tool authoring cookbook](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cookbook/adding-a-tool.md), [subsystem pages](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/core.md)
