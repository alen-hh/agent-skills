---

## name: oclif
description: Use this skill whenever the user wants to create, modify, or maintain a CLI tool using the oclif framework. You MUST trigger this skill when the user mentions "oclif", "build a CLI", "command line tool", or wants to add commands, flags, arguments, or hooks to an existing oclif project, even if they don't explicitly ask for oclif.

# oclif Skill

This skill guides you in building and maintaining CLI tools using the oclif framework.

## 1. Project Scaffolding

Always use the official oclif generators to create projects or add components. Use non-interactive flags to avoid blocking prompts.

- **Create a new project**: `npx oclif generate <cli-name> --yes --module-type ESM --package-manager npm`
- **Initialize in existing project**: `npx oclif init --yes`

## 2. Commands

Commands are classes that extend `@oclif/core`'s `Command`.

- **Generate a command**: `npx oclif generate command <name> --force`
- **Structure**:
  ```typescript
  import {Command, Flags, Args} from '@oclif/core'

  export default class MyCommand extends Command {
    static description = 'describe the command here'
    static examples = [
      '<%= config.bin %> <%= command.id %>',
    ]

    static flags = {
      name: Flags.string({char: 'n', description: 'name to print'}),
      force: Flags.boolean({char: 'f'}),
    }

    static args = {
      file: Args.string({description: 'file to read', required: true}),
    }

    public async run(): Promise<void> {
      const {args, flags} = await this.parse(MyCommand)
      this.log(`hello ${flags.name || 'world'} from ${args.file}`)
    }
  }
  ```

## 3. Flags and Args

- **Flags**: Use `Flags.string()`, `Flags.boolean()`, `Flags.integer()`, etc.
- **Args**: Use `Args.string()`, `Args.integer()`, etc. Set `required: true` if mandatory.
- Always destructure `args` and `flags` from `await this.parse(CommandClass)`.

## 4. Hooks

Hooks allow you to run code at specific lifecycle events (e.g., `init`, `prerun`, `postrun`).

- **Generate a hook**: `npx oclif generate hook <name> --event <event-name> --force`
- Useful for global checks like authentication in `prerun`.

## 5. Configuration (package.json)

The `oclif` object in `package.json` configures the CLI.

- `bin`: The executable name.
- `commands`: Path to compiled commands (usually `./dist/commands`).
- `plugins`: Array of oclif plugins (e.g., `@oclif/plugin-help`).
- `topicSeparator`: Use `:` or  `` (space) to separate topics.

## 6. Best Practices for AI Agents

- **Non-interactive**: Always append `--yes` or `--force` when using `oclif generate` to prevent hanging on prompts. Note: during scaffolding, `oclif generate` might fail at the `oclif readme` step if `node_modules` are not properly installed or paths are relative. This is a known issue. You can safely ignore this error if the project files are generated correctly, but ensure you run `npm install` and `npm run build` inside the generated project directory afterwards.
- **Standard Output**: Use `this.log()` for stdout and `this.error()` for stderr/exiting. Do not use `console.log`.
- **AI-Friendly CLIs**: Design CLIs with clear `--help`, predictable exit codes, and support for stdin pipelines.
- **Testing**: Use `@oclif/test` for writing integration tests.


## 7. Official Documentation Reference
If you need more detailed information about specific oclif features, you can fetch and read the official documentation from the following URLs:

- **Introduction & Basics**:
  - Introduction: https://oclif.github.io/docs/introduction
  - Features: https://oclif.github.io/docs/features
  - Architecture & Base Class: https://oclif.github.io/docs/base_class
- **Commands & Arguments**:
  - Commands: https://oclif.github.io/docs/commands
  - Args: https://oclif.github.io/docs/args
  - Flags: https://oclif.github.io/docs/flags
  - Generator Commands: https://oclif.github.io/docs/generator_commands
- **Project Structure**:
  - Topics: https://oclif.github.io/docs/topics
  - Aliases: https://oclif.github.io/docs/aliases
  - Topic Separator: https://oclif.github.io/docs/topic_separator
  - Single Command CLI: https://oclif.github.io/docs/single_command_cli
  - Flexible Taxonomy: https://oclif.github.io/docs/flexible_taxonomy
- **Advanced Features**:
  - Hooks: https://oclif.github.io/docs/hooks
  - Plugins: https://oclif.github.io/docs/plugins
  - JIT Plugins: https://oclif.github.io/docs/jit_plugins
  - JSON Output: https://oclif.github.io/docs/json
  - Error Handling: https://oclif.github.io/docs/error_handling
  - Logging: https://oclif.github.io/docs/logging
  - Debugging: https://oclif.github.io/docs/debugging
  - Performance: https://oclif.github.io/docs/performance
- **Configuration & Execution**:
  - Config (`package.json`): https://oclif.github.io/docs/config
  - Configuring your CLI: https://oclif.github.io/docs/configuring_your_cli
  - Command Execution: https://oclif.github.io/docs/command_execution
  - Command Discovery Strategies: https://oclif.github.io/docs/command_discovery_strategies
  - Plugin Loading: https://oclif.github.io/docs/plugin_loading
  - ESM Support: https://oclif.github.io/docs/esm
- **Testing & Releasing**:
  - Testing: https://oclif.github.io/docs/testing
  - Releasing: https://oclif.github.io/docs/releasing
  - Running Programmatically: https://oclif.github.io/docs/running_programmatically
- **Customization**:
  - Help Classes: https://oclif.github.io/docs/help_classes
  - Themes: https://oclif.github.io/docs/themes
