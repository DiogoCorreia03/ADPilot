# MCP Client - Interactive Terminal Tool Runner

A dedicated terminal (CLI) application to explore, inspect, and interactively execute tools hosted on the Active Directory penetration testing Model Context Protocol (MCP) Server.

## Features

- **Reuses `mcp-host` Stack**: Connects directly via `util.mcp_session` and `util.config`, automatically inheriting `.env` credentials, network settings, and Ngrok headers.
- **Interactive Tool Browser**:
  - List all loaded MCP tools in a clean, colorized table (`list` / `ls`).
  - Search/filter tools by name or description (`search <term>`).
  - Inspect detailed parameter schemas without executing (`info <tool>`).
- **Guided Schema-Based Parameter Prompting**:
  - Introspects tool schemas, sorting required arguments first.
  - Type-safe validation and casting for `integer`, `boolean`, `enum`, `array`, and `object`.
  - Numbered selection for `enum` fields.
  - Special shortcut inputs during prompting:
    - `:skip` - Skip optional fields.
    - `:null` - Pass explicit null for nullable fields.
    - `:cancel` - Abort argument entry and return to the main menu.
- **Rich Output Formatting**:
  - Highlights executed command syntax in bash.
  - Displays exit code badges (`SUCCESS` vs `FAILED`).
  - Formatted panels for `stdout` and `stderr`.
- **Persistent Session**: Keeps the MCP connection open across multiple tool invocations so you don't reconnect every time you execute a tool.

## Configuration & Environment Variables

You can configure options in a `.env` file (see `.env.example`) or via environment variables:

- `PENTEST_PHASE`: Optional. When set (e.g. `PENTEST_PHASE="shell_only"`), passes `extra_headers={"pentest_phase": "<value>"}` to the MCP session in `util.mcp_session.mcp_tool_session`.

Example `.env`:
```bash
PENTEST_PHASE="shell_only"
```

---

## Installation & Running

From the `mcp-client` directory:

```bash
cd /home/diogo/Coding/temp/mcp-client

# Sync dependencies (installed automatically via uv)
uv sync

# Start the interactive CLI
uv run mcp-cli
# or
uv run python main.py
```

---

## Interactive Commands

| Command | Description |
| :--- | :--- |
| `<number>` | Select and run a tool by index number (e.g. `1`, `5`, `12`) |
| `<tool_name>` | Select tool by name or unique prefix (e.g. `run_dnstool`, `nmap`) |
| `search <query>` / `filter <query>` | Filter the tool table by keyword (e.g. `search dns`, `search kerberos`) |
| `list` / `ls` | Reset search filters and list all available tools |
| `info <tool>` | View full argument documentation and schema for a specific tool |
| `phase [name]` | Show or switch pentest phase and reconnect (e.g. `phase shell_only`, `phase none`) |
| `reconnect` | Re-establish connection with the MCP server |
| `clear` | Clear the terminal screen |
| `help` / `?` | Display command help |
| `exit` / `quit` / `q` | Exit the CLI |

---

## Example Workflow

```text
mcp> search dns
+----+---------------+------------------------------------------------------+---------------+
|  # | Tool Name     | Description                                          | Required Args |
+----+---------------+------------------------------------------------------+---------------+
|  1 | run_dnstool   | Run krbrelayx's dnstool.py to manage AD-integrated... | hostname, ... |
+----+---------------+------------------------------------------------------+---------------+

mcp> 1

Tool: run_dnstool
...
hostname (string) - * REQUIRED
  Hostname/ip or ldap://host:port connection string to connect to.
  Enter hostname: dc01.corp.local

action (string/enum(6)) - * REQUIRED
  Allowed choices:
    [1] add
    [2] modify
    [3] query
    [4] remove
    [5] ressurrect
    [6] ldapdelete
  Enter action: 3

username (string) - * REQUIRED
  Enter username: corp.local\admin

password (string) - * REQUIRED
  Enter password: Password123!

use_kerberos (boolean) - optional [default: False]
  Enter use_kerberos: false

timeout (integer) - optional [default: 120]
  Enter timeout: :skip

Execute run_dnstool? (Y/n): y

Executing run_dnstool...

✔ TOOL EXECUTION SUCCEEDED (exit code 0 in 0.82s)
╭─ Executed Command ─────────────────────────────────────────────────────────╮
│ dnstool.py -u 'corp.local\admin' -p 'Password123!' --action query dc01... │
╰────────────────────────────────────────────────────────────────────────────╯
╭─ Standard Output (stdout) ─────────────────────────────────────────────────╮
│ Found record: dc01.corp.local -> 192.168.122.10                            │
╰────────────────────────────────────────────────────────────────────────────╯
```

---

## Running Unit Tests

```bash
uv run pytest
```
