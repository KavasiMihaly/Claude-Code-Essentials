import json
import os
import sys


def fmt_pct(value):
    try:
        return f"{float(value):.0f}%"
    except (TypeError, ValueError):
        return None


def fmt_tokens(n):
    if n is None:
        return None
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}k"
    return str(n)


def used_tokens(current_usage):
    if not current_usage:
        return None
    keys = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    total = 0
    found = False
    for k in keys:
        v = current_usage.get(k)
        if isinstance(v, (int, float)):
            total += int(v)
            found = True
    return total if found else None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        print("Claude")
        return

    model = (data.get("model") or {}).get("display_name") or "Claude"
    workspace = data.get("workspace") or {}
    cwd = workspace.get("current_dir") or data.get("cwd") or ""
    folder = os.path.basename(cwd.rstrip("/\\")) if cwd else ""

    ctx = data.get("context_window") or {}
    used_pct = fmt_pct(ctx.get("used_percentage"))
    remaining_pct = fmt_pct(ctx.get("remaining_percentage"))
    used_tok = fmt_tokens(used_tokens(ctx.get("current_usage")))
    total_tok = fmt_tokens(ctx.get("context_window_size"))

    ctx_part = None
    if used_tok and total_tok and used_pct:
        ctx_part = f"ctx: {used_tok}/{total_tok} ({used_pct} used)"
    elif used_pct and remaining_pct:
        ctx_part = f"ctx: {used_pct} used / {remaining_pct} left"

    limits = data.get("rate_limits") or {}
    five = fmt_pct((limits.get("five_hour") or {}).get("used_percentage"))
    week = fmt_pct((limits.get("seven_day") or {}).get("used_percentage"))
    limit_bits = []
    if five:
        limit_bits.append(f"5h: {five}")
    if week:
        limit_bits.append(f"7d: {week}")
    limits_part = " ".join(limit_bits) if limit_bits else None

    parts = [model]
    if folder:
        parts.append(folder)
    if ctx_part:
        parts.append(ctx_part)
    if limits_part:
        parts.append(limits_part)

    sys.stdout.write(" | ".join(parts))


if __name__ == "__main__":
    main()
