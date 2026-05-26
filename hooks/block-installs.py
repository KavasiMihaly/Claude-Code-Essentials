#!/usr/bin/env python3
"""
PreToolUse hook: Guard package/software install commands.

Behavior:
- If the command contains "# APPROVED" (case-insensitive), allow it through.
  Claude should append this comment after getting explicit user approval.
- Otherwise, block the command (exit 2) and tell Claude to ask the user first.

Exit 2 = block the command and send feedback to Claude.
Exit 0 = allow the command.
"""

import json
import re
import sys


# Patterns that indicate an install command
INSTALL_PATTERNS = [
    # Node.js / JavaScript
    r'\bnpm\s+install\b',
    r'\bnpm\s+i\b',
    r'\bnpx\s+',              # npx can auto-install packages
    r'\byarn\s+add\b',
    r'\byarn\s+install\b',
    r'\bpnpm\s+(add|install)\b',
    r'\bbun\s+(add|install)\b',
    # Python
    r'\bpip\s+install\b',
    r'\bpip3\s+install\b',
    r'\bpipx?\s+install\b',
    r'\buv\s+(pip\s+install|add|tool\s+install)\b',
    r'\bpoetry\s+add\b',
    r'\bconda\s+install\b',
    # Windows package managers
    r'\bwinget\s+install\b',
    r'\bchoco\s+install\b',
    r'\bscoop\s+install\b',
    # Linux package managers
    r'\bapt(-get)?\s+install\b',
    r'\byum\s+install\b',
    r'\bdnf\s+install\b',
    r'\bpacman\s+-S\b',
    r'\bbrew\s+install\b',
    # .NET / NuGet
    r'\bdotnet\s+(add|tool\s+install)\b',
    r'\bnuget\s+install\b',
    # Rust / Go / Ruby
    r'\bcargo\s+install\b',
    r'\bgo\s+install\b',
    r'\bgem\s+install\b',
    # Generic
    r'\bcurl\s+.*\|\s*(bash|sh)\b',   # curl pipe to shell (installer scripts)
    r'\bwget\s+.*\|\s*(bash|sh)\b',
]

# Marker that Claude appends after getting explicit user approval
APPROVAL_MARKER = re.compile(r'#\s*APPROVED', re.IGNORECASE)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)  # Can't parse input, allow

    tool_name = data.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    # Check if this is an install command
    matched_text = None
    for pattern in INSTALL_PATTERNS:
        match = re.search(pattern, command, re.IGNORECASE)
        if match:
            matched_text = match.group(0)
            break

    if not matched_text:
        sys.exit(0)  # Not an install command, allow

    # Install command detected — check for approval marker
    if APPROVAL_MARKER.search(command):
        sys.exit(0)  # Approved, allow through

    # No approval marker — block and instruct Claude
    msg = (
        f"BLOCKED: Install command detected ({matched_text}). "
        f"You must explain to the user what package(s) will be installed, "
        f"why they are needed, and get explicit approval before running. "
        f"Once approved, append ' # APPROVED' to the end of the command to bypass this check."
    )
    print(msg, file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
