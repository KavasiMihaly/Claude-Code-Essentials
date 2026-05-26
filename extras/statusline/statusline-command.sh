#!/bin/sh
input=$(cat)
model=$(echo "$input" | jq -r '.model.display_name // "Claude"')
cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
dir=$(basename "$cwd")
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
remaining=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')

if [ -n "$used" ] && [ -n "$remaining" ]; then
    ctx=$(printf "ctx: %.0f%% used / %.0f%% left" "$used" "$remaining")
else
    ctx=""
fi

five=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
week=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // empty')
limits=""
if [ -n "$five" ]; then
    limits=$(printf "5h: %.0f%%" "$five")
fi
if [ -n "$week" ]; then
    w=$(printf "7d: %.0f%%" "$week")
    if [ -n "$limits" ]; then
        limits="$limits $w"
    else
        limits="$w"
    fi
fi

parts="$model | $dir"
if [ -n "$ctx" ]; then
    parts="$parts | $ctx"
fi
if [ -n "$limits" ]; then
    parts="$parts | $limits"
fi

printf "%s" "$parts"
