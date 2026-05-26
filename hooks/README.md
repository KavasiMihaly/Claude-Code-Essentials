# Hooks

Two PreToolUse / lifecycle hooks bundled with this plugin. Wired automatically via `.claude-plugin/plugin.json` when you `/plugin install` the marketplace entry.

## `agent-logger.py`

Logs every Claude Code session to `<your-repo>/_Agent Logs/` as JSONL — one file per session, plus a `sessions-index.jsonl` summary.

**Captures:**
- `SessionStart` / `SessionEnd` (model, source, cwd, permission mode)
- `UserPromptSubmit` (prompt text, truncated, redacted if sensitive)
- `PreToolUse` / `PostToolUse` (tool name + human-readable summary + safe details)
- `PostToolUseFailure` (errors and interrupts)
- `SubagentStart` / `SubagentStop` (agent id + type)
- `Stop` (turn boundaries)

**Safety:**
- Never logs file content from `Write` / `Edit` — only paths.
- Redacts file paths matching `.env`, `credentials`, `secrets`, `id_rsa`, `.pem`, `.key`, `password`, `token`, `api_key`, `apikey`.
- Redacts prompts containing the same patterns.
- Truncates long fields to 500 chars (`...[truncated]`).

**Side effect (first session in a repo):** Creates `_Agent Logs/` and drops a `.gitignore` inside it (`*\n!.gitignore`) so log files are ignored by default but the rule travels with the repo.

**Output:**

```jsonl
{"ts":"2026-05-26T14:32:11Z","event":"SessionStart","session_id":"a1b2c3d4","source":"startup","model":"claude-opus-4-7","cwd":"/path/to/repo","permission_mode":"default"}
{"ts":"2026-05-26T14:32:15Z","event":"UserPromptSubmit","session_id":"a1b2c3d4","prompt":"refactor the auth middleware"}
{"ts":"2026-05-26T14:32:18Z","event":"PreToolUse","session_id":"a1b2c3d4","tool":"Read","summary":"read → src/auth.ts","details":{"file_path":"src/auth.ts"}}
```

## `block-installs.py`

PreToolUse guard wired to the `Bash` tool. Catches package-install commands and blocks them with `exit 2` unless explicitly approved.

**Triggers on:** `npm install`, `pip install`, `pnpm add`, `yarn add`, `choco install`, `winget install`, `brew install`, `cargo install`, `gem install`, `apt install`, and similar.

**The approval flow:**

1. Claude tries `pip install dbt-core` → hook blocks with `exit 2`.
2. Claude sees the rejection and asks you for permission, explaining what the package does.
3. You say yes.
4. Claude re-runs as `pip install dbt-core # APPROVED` — the marker bypasses the hook.

The marker is case-insensitive and matched as a substring (`# approved`, `# APPROVED`, ` // APPROVED `, etc. all work).

**Why this exists:** Stops agents from silently pulling in dependencies you didn't sanction during agentic loops. A single missed `npm install some-typo-squatted-package` can compromise an entire environment.

## Disabling a hook

Both hooks are wired in `../.claude-plugin/plugin.json`. To disable one without uninstalling the plugin, fork this repo and remove its entry from the `hooks` section of `plugin.json`, then point your marketplace at the fork.

## Editing locally

If you've cloned this repo for development:

```bash
# Edit the hook
$EDITOR hooks/agent-logger.py

# Restart Claude Code — hooks snapshot at session start
```
