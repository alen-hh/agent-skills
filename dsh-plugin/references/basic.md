# Basic plugin path

Use this file to create a plugin, register a tool, accept configuration, and ship a bundle. Start from a Harness checkout that can run `pnpm dsh`, or from an installed `dsh` CLI when packaging.

## 1. Minimal plugin

A plugin is a module that exports `apply`. The loader calls it with `ctx`:

```ts
import type { Context } from '@deepseek-ai/cordis'

export const name = 'hello-plugin'

export function apply(ctx: Context) {
  console.log('[hello-plugin] plugin loaded!')
}
```

Function form is the default. Object form (`export default { name, inject, apply }`) is equivalent. Class form (`extends Service`) is for providing a service — see [framework.md](framework.md).

### Local load via `--patch`

From the Harness repository root:

```sh
mkdir -p scratch-plugin/src
pwd   # use this absolute path in the overlay
```

`scratch-plugin/cordis.yml`:

```yaml
- insert:
    - id: hello
      name: '/absolute/path/to/deepseek-harness/scratch-plugin/src/my-plugin.ts'
```

The `name` path **must be absolute**. A patch contributes rows; it does not change the profile directory used to resolve modules.

```sh
pnpm dsh web --patch ./scratch-plugin/cordis.yml
```

Open `http://127.0.0.1:3080`. The process log should print the load message.

### Dependencies

If the plugin uses `tools`, `llm`, or any other service, declare `inject` so Cordis waits:

```ts
export const inject = ['tools']

export function apply(ctx: Context) {
  // ctx.tools is ready here.
}
```

### Cleanup

Registrations made through `ctx` unwind on unload. For a resource you create yourself, return a disposer:

```ts
export function apply(ctx: Context) {
  ctx.effect(() => {
    const timer = setInterval(() => {
      console.log('heartbeat')
    }, 5000)
    return () => clearInterval(timer)
  })
}
```

## 2. Register a tool

`inject` the tool registry and register with `defineTool`. `execute` returns the canonical value described by `output.schema`; `output.render` turns that value into model-facing content.

```ts
import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'greet-tool'
export const inject = ['tools']

export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'greet',
    description: 'Greet someone by name.',
    parameters: {
      name: { type: 'string', required: true, description: 'The name to greet' },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      return `Hello, ${args.name}!`
    },
  }))
}
```

Reload with the same `--patch` overlay and ask the Web UI to call the tool.

For nested schemas, background work, policy hooks, Code Mode, or UI cards, fetch the [tool authoring cookbook](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/cookbook/adding-a-tool.md). Do not invent a second tool DSL.

A simple tool stays in one plugin. Split into three packages only when the capability needs replaceable providers — [practice.md](practice.md).

## 3. Plugin configuration

Export a `Config` type and a **same-named Schemastery schema**. Put defaults on the schema fields. Cordis validates on load and fills defaults.

```ts
import type { Context } from '@deepseek-ai/cordis'
import Schema from '@deepseek-ai/schemastery'

export const name = 'my-plugin'

export interface Config {
  greeting: string
  maxRetries: number
  verbose?: boolean
}

export const Config: Schema<Config> = Schema.object({
  greeting: Schema.string().default('Hello'),
  maxRetries: Schema.number().default(3),
  verbose: Schema.boolean().default(false),
})

export function apply(ctx: Context, config: Config) {
  console.log(config.greeting)
}
```

Wrong: `export const Config = { greeting: 'Hello' }` — a plain object is not a Standard Schema, so Cordis will not validate or default it.

Stricter fields:

```ts
export const Config = Schema.object({
  apiKey: Schema.string().required(),
  timeout: Schema.number().default(30000),
  mode: Schema.union(['fast', 'accurate']).default('fast'),
})
```

Invalid configuration must fail the plugin load with an actionable error. Do not wait until the first request.

**Tunable values belong in config.** If two deployments might disagree (timeouts, endpoints, feature flags, greeting text), it is a `Config` field. The test: can `cordis.yml` change it without a code edit?

Overlay config on the inserted row:

```yaml
- insert:
    - id: hello
      name: './src/my-plugin.ts'
      config:
        greeting: 'Hi there'
        maxRetries: 5
```

(Use an absolute `name` for local `--patch` development, as in section 1.)

Editing config hot-replaces the plugin: old registrations dispose, then the new `apply` runs.

## 4. Package and install a bundle

A **bundle** is an npm package that ships a configuration layer (`dsh.bundle`). A **profile** is a directory under `$DSH_HOME/profiles/<name>` that lists which bundles compose a runnable setup (`dsh.profile`). You author bundles. `dsh plugin` creates and maintains profiles — do not write a profile `package.json` by hand.

### Bundle layout

```
hello-plugin/
├── package.json
├── cordis.patch.yml
└── index.js
```

`package.json`:

```json
{
  "name": "dsh-hello-plugin",
  "version": "0.1.0",
  "type": "module",
  "main": "index.js",
  "files": ["index.js", "cordis.patch.yml"],
  "dsh": { "bundle": { "patch": "./cordis.patch.yml" } }
}
```

Without `dsh.bundle`, `dsh plugin` installs a plain dependency and prints a warning. Use that shape for libraries, not for plugins users enable.

`cordis.patch.yml` — same YAML array as `--patch` overlays, but `name` is the package name so Node resolution works after install:

```yaml
- insert:
    - id: hello
      name: dsh-hello-plugin
```

### Install into a profile

`dsh plugin --profile <name> <args…>` forwards to pnpm inside the profile directory.

```sh
dsh plugin --profile demo add ./hello-plugin
dsh --profile demo --dump-config    # look for "# == dsh-hello-plugin"
dsh --profile demo
```

`dsh plugin --profile demo remove dsh-hello-plugin` removes the dependency and the layer.

From a Harness source checkout, prefix with `pnpm` (`pnpm dsh plugin …`) and keep the package at the repo root as the tutorials do.

### Layer order

Effective config starts empty, then applies:

1. Each bundle in `dsh.profile.bundles`, in list order (`@deepseek-ai/dsh-base` first)
2. The profile's own `cordis.patch.yml`
3. Home-level `$DSH_HOME/cordis.patch.yml`
4. Each `--patch` overlay, in argv order

Later layers win **per row**. A patch replaces a row's entire `config` by `id` — it does not deep-merge. If you override an earlier row, restate every key that row still needs. Prefer schema defaults so users only patch what they change.

In-box bundle names resolve from the dsh installation. pnpm only manages out-of-tree packages, so your bundle can assume `@deepseek-ai/dsh-base` is present.

### Surface CLI flags (optional)

A bundle that owns a runnable app mounts a provider plugin with `inject = ['cmdlineArgs']`, parses with `parseCmdline` from `@deepseek-ai/dsh-cmdline`, and exposes an app-owned service. Other rows inject that service and read `!!js` options (`ctx.myAppStartup.port ?? 8080`). On `--help` the provider publishes no service, so those rows never activate. Fetch the [CLI reference](https://github.com/deepseek-ai/deepseek-harness/blob/master/apps/cli/reference/README.md) when implementing this.

### Git installs and `prepare`

```sh
dsh plugin --profile demo add github:you/hello-plugin
```

Git installs fetch **source**, not `lib/`. `build` does not run. Authors ship a self-contained `prepare` script (no sibling-monorepo assumptions). [turtle-ui](https://github.com/deepseek-harness/turtle-ui) is the working example: `prepare` runs a dedicated tsdown config without project references or type checking.

pnpm ≥10 refuses a git dependency's `prepare` until the user allowlists it in the profile `pnpm-workspace.yaml`:

```yaml
allowBuilds:
  dsh-hello-plugin: true
```

Then re-run `add`. That allowance executes the package's code at install time, outside the agent sandbox. Pin a commit (`github:you/hello-plugin#<sha>`). Only allow packages you trust.

To avoid the allowance, publish built artifacts: `pnpm publish` with `lib/` already built, or `pnpm pack` and `dsh plugin add ./pkg-0.1.0.tgz`.
