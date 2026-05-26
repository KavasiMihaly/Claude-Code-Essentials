# Statusline

A token-aware status bar for Claude Code. Shows the current model, working folder, context-window consumption, and rate-limit usage in one line.

```
Claude Opus 4.7 | my-project | ctx: 45.2k/200.0k (23% used) | 5h: 12% 7d: 4%
```

## Why it's in `extras/` (not auto-installed)

The statusline is a **global Claude Code setting**, configured in `~/.claude/settings.json` under the `statusLine` key. It can't be wired by a plugin install — you set it once at the user level and it applies to every project.

## Install

### Option A — Python (recommended)

1. Copy `statusline-command.py` to `~/.claude/statusline-command.py`.

2. Add this block to `~/.claude/settings.json`:

   ```json
   "statusLine": {
     "type": "command",
     "command": "python ~/.claude/statusline-command.py"
   }
   ```

   On **Windows**, use the explicit Python path and forward slashes (tilde and Git Bash paths don't expand reliably in hook contexts):

   ```json
   "statusLine": {
     "type": "command",
     "command": "C:/Python313/python.exe C:/Users/<your-username>/.claude/statusline-command.py"
   }
   ```

3. Restart Claude Code.

### Option B — Shell (`jq`)

If you'd rather not depend on Python:

1. Copy `statusline-command.sh` to `~/.claude/statusline-command.sh` and `chmod +x` it.

2. In `~/.claude/settings.json`:

   ```json
   "statusLine": {
     "type": "command",
     "command": "sh ~/.claude/statusline-command.sh"
   }
   ```

3. Requires `jq` on `PATH`.

## What it shows

The script reads JSON from stdin (Claude Code provides: `model`, `workspace`, `context_window`, `rate_limits`) and prints a single pipe-separated line:

| Segment | Source field | Example |
|---|---|---|
| Model | `model.display_name` | `Claude Opus 4.7` |
| Folder | `workspace.current_dir` (basename) | `my-project` |
| Context window | `context_window.current_usage` + `.context_window_size` | `ctx: 45.2k/200.0k (23% used)` |
| 5-hour rate limit | `rate_limits.five_hour.used_percentage` | `5h: 12%` |
| 7-day rate limit | `rate_limits.seven_day.used_percentage` | `7d: 4%` |

Missing fields are silently dropped — if Claude Code doesn't provide rate limits, only the first three segments render.

## Customize

`statusline-command.py` is 83 lines, no dependencies. Fork it to add what you want:

- Git branch (call `git rev-parse --abbrev-ref HEAD` and append)
- Time of day
- A health-status emoji based on context usage thresholds
- Custom color codes via ANSI escapes

PRs welcome.
