# Framework: lifecycle, services, events

Use this file when the plugin participates in load/unload, exposes or consumes a `ctx.*` service, or communicates through Cordis events.

## Lifecycle

Every loaded plugin owns a Fiber:

```
PENDING → LOADING → ACTIVE
                 ↘ FAILED
ACTIVE → UNLOADING → DISPOSED
```

| State | Meaning |
|-------|---------|
| PENDING | Declared; required services are not ready |
| LOADING | `apply` is running |
| ACTIVE | Running |
| FAILED | `apply` threw |
| UNLOADING | Disposing resources |
| DISPOSED | Fully unloaded |

`inject` drives loading. The plugin stays PENDING until every required service exists. If a required service disappears (provider replacement), dependents unload (`ACTIVE → DISPOSED`) and load again when it returns. That is why you declare `inject` instead of polling `ctx.get` for required capabilities.

### What unload undoes

These are tracked and disposed:

- `ctx.on(event, handler)`
- `ctx.tools.register(tool)`
- `ctx.llm.registerAdapter(names, adapter)`
- `ctx.effect(() => cleanup)`

Disposer **invocation** starts in reverse registration order, but multiple **async** disposers run concurrently with no serial completion guarantee. Put order-dependent cleanup in one `ctx.effect()` and `await` the steps there.

### Nested plugins and dispose

`ctx.plugin(child)` creates a child Fiber. It inherits the parent context and unloads with the parent.

```ts
const fiber = ctx.plugin(myPlugin)
await fiber.dispose()
```

`dispose` removes this plugin's registrations, recursively unloads children, and resolves after asynchronous cleanup finishes.

### HMR

With `@deepseek-ai/cordis-plugin-hmr` in the composition, editing a source file unloads the old instance (cleanup runs) then loads the new `apply`. Effects make replacement safe; leaked `setInterval` without `ctx.effect` does not.

## Services

A service is a named capability on `ctx` (`ctx.tools`, `ctx.llm`, `ctx.agents`). Plugins provide services; other plugins consume them by name, not by importing an implementation.

### Consume

```ts
export const inject = ['tools']

export function apply(ctx: Context) {
  ctx.tools.register(/* ... */)
}
```

Required: list the name in `inject` — the plugin does not load while the service is absent.

Optional: skip `inject` and use `ctx.get` at the use site:

```ts
export function apply(ctx: Context) {
  const metrics = ctx.get('metrics')
  metrics?.record('plugin_loaded', 1)
}
```

### Provide

Extend `Service`, pass the service name to `super`, and merge the type onto `Context`:

```ts
import { Service, type Context } from '@deepseek-ai/cordis'

declare module '@deepseek-ai/cordis' {
  interface Context {
    metrics: MetricsService
  }
}

export default class MetricsService extends Service {
  static inject = ['llm']

  constructor(ctx: Context) {
    super(ctx, 'metrics')
  }

  record(event: string, value: number) {
    // ...
  }
}
```

Consumers then `inject: ['metrics']` and call `ctx.metrics.record(...)`.

Do not maintain a handwritten catalog of built-in Harness services. Use the generated `cordis-surface` regions on the [subsystem pages](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/subsystems/core.md) and the TypeScript interfaces.

### Isolation

`cordis.yml` can isolate a service so sibling groups see separate instances:

```yaml
- id: group-a
  name: '@deepseek-ai/cordis-plugin-group'
  group: true
  isolate:
    shell: true
  config:
    - name: '@deepseek-ai/dsh-bash-local'
      config:
        timeoutMs: 5000
    - name: './src/plugin-a.ts'
```

Each group gets its own `shell`. Use this when two plugins must not share the same provider instance (different timeouts, different credentials).

## Events

Events are the loose-coupling extension point. Prefer events for interception and policy; prefer service methods for direct capability calls.

### Listen and emit

```ts
ctx.on('event-name', (payload) => { /* ... */ })
ctx.emit('event-name', payload)
```

Listeners registered with `ctx.on` are effects — they are removed when the plugin unloads. Do not pair them with a manual `off`.

### Modes

Pick the mode that matches the contract. New harness events document mode with `@mode` so generated catalogs can check dispatch sites.

**emit — broadcast.** Every listener runs synchronously. Return values are ignored.

**bail — first defined result wins.** Listeners run in order. The first value other than `null`, `false`, or `undefined` is the result. Return those sentinels to keep going.

**serial — ordered and awaited.** Same short-circuit as bail, but async results are awaited.

**waterfall — pipeline.** Each listener receives `(...args, next)`. **Call `next()` to delegate.** Omitting `next()` short-circuits. That is how gateways and policy interceptors work — not a missing `await`. Cooperative listeners mutate a shared object and then delegate.

```ts
const output = await ctx.waterfall('my-plugin/transform', input, async () => input)

ctx.on('my-plugin/transform', async (_input, next) => {
  const downstream = await next()
  return downstream.trim()
})
```

### Typed events

Declaration-merge into `Events`. This is types only — you still `emit` / `on` at runtime.

```ts
import '@deepseek-ai/cordis'

declare module '@deepseek-ai/cordis' {
  interface Events {
    'my-plugin/ready': (payload: { id: string }) => void
    'my-plugin/check': (input: string) => boolean | undefined
    'my-plugin/transform': (input: string, next: () => Promise<string>) => Promise<string>
  }
}
```

Harness Cordis names look like `namespace/action`: `agent/step`, `agent/request`, `agent/request-error`, `tools/result`, `session/event`. Fetch subsystem pages for exact signatures.

`turn/*`, `step/*`, `tool/call`, `tool/result`, and `compaction/*` are **durable session-event types**, not Cordis events of those names. Observe them by listening to `session/event` and reading `event.type`.

### Example: log tool results

```ts
import type { Context } from '@deepseek-ai/cordis'
import '@deepseek-ai/dsh-tools'

export const name = 'tool-logger'

export function apply(ctx: Context) {
  ctx.on('tools/result', (exec, result) => {
    console.log(`[tool] ${exec.name}(${JSON.stringify(exec.arguments)})`)
    const text = result.content
      .map(block => block.type === 'text' ? block.text : '')
      .join('')
    console.log(`[tool result] ${text.slice(0, 100)}`)
  })
}
```
