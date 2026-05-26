# Extras

Tools that ship with this plugin but can't be wired by `/plugin install` because they configure global Claude Code settings rather than per-plugin hooks.

| Folder | What it is |
|---|---|
| [`statusline/`](statusline/) | Token-aware status bar (model, folder, context window, rate limits). Wires via `~/.claude/settings.json` → `statusLine`. |

Each folder has its own README with copy-paste install steps.
