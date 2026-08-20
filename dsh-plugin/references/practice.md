# Practice: capability layering and LLM adapters

Use this file for replaceable capabilities (Bash-style seams) and for connecting a new model provider. Complete the [basic](basic.md) path and [services](framework.md) first.

## Three-role capability design

When a capability is general enough to need **replaceable providers**, Harness splits three roles. Put them in separate packages only when the roles must evolve or be replaced independently. A package may own more than one role. The complete capability is the seam; no single role is.

Do **not** split preemptively. A one-off tool plugin stays one package.

| Role | Owns | Example |
|------|------|---------|
| Service Definition | Cordis service + Request/Result types | `dsh-shell` |
| Service Provider | One implementation of that service | `dsh-bash-local` |
| Consumer | How the model sees the capability (usually a tool) | `dsh-tool-bash` |

```
Service Definition  <──  Service Provider
        ▲
        └── Consumer  (injects the service name, never the provider package)
```

The provider and the consumer both depend on the definition. They **do not** depend on each other. Swapping the provider in `cordis.yml` leaves the definition and the tool unchanged.

Built-in families and package links live in the [capability-seam reference](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/capability-seams.md). Fetch it when matching an existing seam rather than inventing a parallel one.

### Step 1 — Service Definition

```ts
import { Service, type Context } from '@deepseek-ai/cordis'

declare module '@deepseek-ai/cordis' {
  interface Context {
    myCap: MyCapService
  }
}

export abstract class MyCapService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'myCap')
  }

  abstract execute(request: MyCapRequest): Promise<MyCapResult>
}

export interface MyCapRequest {
  input: string
}

export interface MyCapResult {
  output: string
}
```

The definition package owns Request/Result types. Resolve defaults in an explicit `resolve(request): Spec` step rather than hiding `?? default` inside `run()`.

### Step 2 — Service Provider

```ts
import type { Context } from '@deepseek-ai/cordis'
import { MyCapService, type MyCapRequest, type MyCapResult } from '@deepseek-ai/dsh-my-cap'

class MyCapLocal extends MyCapService {
  async execute(request: MyCapRequest): Promise<MyCapResult> {
    return { output: request.input.toUpperCase() }
  }
}

export const name = 'my-cap-local'

export function apply(ctx: Context) {
  ctx.plugin(MyCapLocal)
}
```

### Step 3 — Consumer (tool)

```ts
import type { Context } from '@deepseek-ai/cordis'
import { defineTool } from '@deepseek-ai/dsh-tools'

export const name = 'tool-my-cap'
export const inject = ['tools', 'myCap']

export function apply(ctx: Context) {
  ctx.tools.register(defineTool({
    name: 'my_cap',
    description: 'Execute my capability.',
    parameters: {
      input: { type: 'string', required: true },
    },
    output: {
      schema: { type: 'string' },
      render: (_args, value) => [{ type: 'text', text: value }],
    },
    async execute(args) {
      const result = await ctx.myCap.execute({ input: args.input })
      return result.output
    },
  }))
}
```

Compose provider + consumer in `cordis.yml` (the definition is typically pulled in by the provider):

```yaml
- name: '@deepseek-ai/dsh-my-cap-local'
- name: '@deepseek-ai/dsh-tool-my-cap'
```

## LLM adapters

An adapter extends `LlmAdapter` and implements `stream()`: translate Harness `GenerateOptions` into the provider API, then yield Harness `StreamChunk` values.

Treat `@deepseek-ai/dsh-llm` TypeScript types as authoritative. Map supported fields; if the provider cannot honor a field, throw `LlmError` with a stable code instead of silently dropping it.

### Plugin wrapper

```ts
import type { Context } from '@deepseek-ai/cordis'
import Schema from '@deepseek-ai/schemastery'
import { LlmAdapter, type GenerateOptions, type StreamChunk } from '@deepseek-ai/dsh-llm'

class MyAdapter extends LlmAdapter {
  constructor(private readonly apiKey: string) {
    super()
  }

  async *stream(options: GenerateOptions): AsyncIterable<StreamChunk> {
    // 1. Convert options.messages to the provider format.
    // 2. Call the streaming API (forward options.signal).
    // 3. Yield StreamChunk values (see protocol below).
  }
}

export interface Config {
  apiKey: string
  providers: string[]
}

export const Config: Schema<Config> = Schema.object({
  apiKey: Schema.string().required(),
  providers: Schema.array(Schema.string()).required(),
})

export const name = 'my-llm-adapter'
export const inject = ['llm']

export function apply(ctx: Context, config: Config) {
  ctx.llm.registerAdapter(config.providers, new MyAdapter(config.apiKey))
}
```

`registerAdapter`'s first argument is the list of provider routes this adapter handles. `GenerateOptions.provider` selects the adapter; `GenerateOptions.model` is an adapter-owned model id and is not lifecycle-registered. Override `listModels()` when selectors should show choices.

Override `resolveModel(provider, model, signal?)` to return exact provider/model identity plus optional `context` and `reasoning` metadata. Preserve the adapter's selectable reasoning list (including `off` when the upstream API returns it) rather than promoting values into a core enum. Honor `signal` so cancellation reaches quiescence. Omitting `reasoning` means that model has no selectable reasoning-effort capability.

### StreamChunk protocol

```ts
import { CallId, type StreamChunk } from '@deepseek-ai/dsh-llm'

async function* exampleChunks(): AsyncIterable<StreamChunk> {
  yield { type: 'block-start', index: 0, blockType: 'text' }
  yield { type: 'text-delta', index: 0, text: 'Hello' }
  yield { type: 'text-delta', index: 0, text: ' world' }
  yield {
    type: 'block-end',
    index: 0,
    block: { type: 'text', text: 'Hello world' },
  }

  yield { type: 'block-start', index: 1, blockType: 'tool-call' }
  yield {
    type: 'tool-call-delta',
    index: 1,
    id: CallId('call-123'),
    name: 'bash',
    argumentsDelta: '{"command":"ls"}',
  }
  yield {
    type: 'block-end',
    index: 1,
    block: {
      type: 'tool-call',
      id: CallId('call-123'),
      name: 'bash',
      arguments: '{"command":"ls"}',
    },
  }

  yield { type: 'usage', usage: { inputTokens: 100, outputTokens: 50 } }
  yield { type: 'finish', reason: { kind: 'stop' } }
  // { kind: 'tool-calls' } asks the loop to execute tools.
}
```

Rules:

- Every `block-start` has a matching `block-end`.
- `index` increases from 0 and identifies content-block order.
- `tool-call-delta.argumentsDelta` is raw JSON text, sent whole or split across chunks.
- Emit `usage` before `finish`.
- `finish` is the final chunk.

### Errors, headers, abort

Throw transport and protocol failures as `LlmError` with a stable code. The agent loop does not convert a plain `Error`. Every provider HTTP request must merge `attributionHeaders()` and forward `options.signal`.

```ts
import {
  attributionHeaders,
  LlmAdapter,
  LlmError,
  type GenerateOptions,
  type StreamChunk,
} from '@deepseek-ai/dsh-llm'

class HttpAdapter extends LlmAdapter {
  constructor(private readonly endpoint: string) {
    super()
  }

  async *stream(options: GenerateOptions): AsyncIterable<StreamChunk> {
    const response = await fetch(this.endpoint, {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        ...attributionHeaders(),
      },
      body: JSON.stringify({ model: options.model, messages: options.messages }),
      ...options.signal ? { signal: options.signal } : {},
    })
    if (!response.ok) {
      throw new LlmError(`Provider API error: ${response.status}`, 'PROVIDER_HTTP_ERROR')
    }
    yield { type: 'finish', reason: { kind: 'stop' } }
  }
}
```

### Wire it in cordis.yml

```yaml
- id: my-llm
  name: './src/my-llm-adapter.ts'
  config:
    apiKey: !!js process.env.MY_API_KEY
    providers:
      - my-provider

- id: agent-loop
  name: '@deepseek-ai/dsh-agent-loop'
  config:
    agents:
      - id: main
        provider: my-provider
        model: my-model-v1
```

Local `--patch` still needs an absolute `name` path; a shipped bundle uses the package name in `cordis.patch.yml`.

Reference implementations in the Harness repo: `packages/llm/llm-deepseek/` (OpenAI-compatible) and `packages/llm/llm-pi-ai/` (different SDK). Compare those two when translating a new provider.
