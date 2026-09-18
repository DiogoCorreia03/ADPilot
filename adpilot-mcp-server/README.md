# ADPilot MCP Server

> **Model Context Protocol (MCP) Server for Automated Active Directory Pentesting**

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![FastMCP](https://img.shields.io/badge/framework-FastMCP-brightgreen.svg)](https://github.com/jlowin/fastmcp)
[![Docker](https://img.shields.io/badge/deployment-docker--compose-blue.svg)](compose.yaml)
[![License](<https://img.shields.io/badge/license-Proprietary%20%2F%20Research-red.svg>)](#disclaimer)

**ADPilot MCP Server** is a specialized Model Context Protocol (MCP) interface that bridges Large Language Models (LLMs) to an offensive security toolset for automated penetration testing of Windows Active Directory (WAD) environments.

The server runs on an attacker machine (typically a customized Ubuntu Linux container) and exposes structured MCP tools, resources, and playbooks. It features dynamic tool filtering based on pentest phase, state/credential persistence, process group lifecycle management, and strict execution guardrails.

---

## Pentest Phases & Methodology

ADPilot structures Active Directory penetration tests into standard phases defined in `PentestPhase`, plus a dedicated shell-only mode:

| Phase                                   | Identifier                                    | Focus                                                                         | Key Tools                                                                                                                                                          |
| --------------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **1. External Reconnaissance**    | `external_reconnaissance`                   | Perimeter mapping, port scanning, DNS resolution, initial user enumeration    | `run_nmap_scan`, `run_nslookup`, `run_curl`, `run_kerbrute`, `run_smbclient`                                                                             |
| **2. Initial Access**             | `initial_access`                            | Unauthenticated / pre-auth roasting, password spraying, hash cracking         | `run_getnpusers`, `run_getuserspns`, `run_kerbrute`, `run_hashcat`, `run_smbclient`                                                                      |
| **3. Internal Reconnaissance**    | `internal_reconnaissance`                   | LDAP/AD queries, delegation discovery, RID cycling, BloodHound collection     | `run_nmap_scan`, `run_ldapsearch`, `run_ldap_dump`, `run_getadusers`, `run_finddelegation`, `run_lookupsid`, `run_smbclient`                         |
| **4. Lateral Movement & PrivEsc** | `lateral_movement_and_privilege_escalation` | Remote command execution, credential extraction, AD CS abuse, Kerberos relays | `run_secretsdump`, `run_wmiexec`, `run_psexec`, `run_mssqlclient`, `run_certipy`, `run_getst`, `run_ticketer`, `run_ntlmrelayx`, `run_smbclient` |
| **5. Check Results**              | `check_results`                             | Review captured credentials, audit persistence, flag inspection               | `credentials_get`, `credentials_add`, `ad://state/credentials`                                                                                               |
| **6. Shell Only**                 | `shell_only` (or `shell_exec`)              | Direct arbitrary command execution only                                        | `shell_exec`                                                                                                                                                       |

### Dynamic Phase Filtering & Guardrails

The server includes a `ToolFilterMiddleware` that dynamically limits the tools exposed to the agent based on the client HTTP header `pentest_phase` (or `pentest-phase`):

- **Tool Listing**: Only tools relevant to the active pentest phase are exposed in `tools/list`, keeping the model's context focused and concise.
- **Shell-Only Mode**: Passing `pentest_phase: shell_only` (or `shell_exec`) filters exposed tools down strictly to `shell_exec`.
- **Credential Operations**: Credential management tools (`credentials_add`, `credentials_get`) are accessible across standard pentest phases for the Checker agent.


---

## Tool Suites

### 1. Reconnaissance (`mcp/tools/recon.py`)

- `run_nmap_scan`: Network port and service scanning on hosts and CIDR ranges.
- `run_nslookup`: DNS enumeration (supports `A`, `SRV`, `TXT`, `MX`, `NS`, `PTR`).
- `run_curl`: HTTP/REST requests against web interfaces and APIs.

### 2. Active Directory Enumeration (`mcp/tools/ad_enum.py`)

- `run_netexec`: NetExec (`nxc`) multi-protocol enumeration (SMB, LDAP, WinRM, MSSQL, etc.).
- `run_smbclient`: SMB/CIFS share browsing and file transfers.
- `run_ldapsearch`: Direct LDAP/LDAPS queries with custom filters and base DNs.
- `run_ldap_dump`: Automated domain dump via `ldapdomaindump`.
- `run_getadusers`: Comprehensive AD user and attribute enumeration (`GetADUsers.py`).
- `run_finddelegation`: Identify unconstrained, constrained, and RBCD delegation paths (`findDelegation.py`).
- `run_lookupsid`: Enumerate domain accounts and SIDs via RID cycling (`lookupsid.py`).

### 3. Kerberos Operations (`mcp/tools/kerberos.py`)

- `run_kerbrute`: Fast Kerberos-based user enumeration, password spraying, and brute-forcing.
- `run_getnpusers`: AS-REP roasting against accounts with Kerberos pre-authentication disabled (`GetNPUsers.py`).
- `run_getuserspns`: Kerberoasting service principal names (`GetUserSPNs.py`).
- `run_gettgt`: Request Kerberos Ticket Granting Tickets with passwords, hashes, or AES keys (`getTGT.py`).
- `run_getst`: Request Service Tickets (TGS) with S4U impersonation for constrained delegation (`getST.py`).
- `run_ticketer`: Forge Golden/Silver Kerberos tickets (`ticketer.py`).
- `run_hashcat`: GPU/CPU password hash cracking for captured AS-REP and Kerberoast hashes.

### 4. Lateral Movement & Abuse (`mcp/tools/lateral.py`)

- `run_secretsdump`: Remote credential extraction from SAM, LSA, NTDS.dit, and Kerberos keys (`secretsdump.py`).
- `run_wmiexec`: Remote command execution via WMI.
- `run_mssqlclient`: MSSQL database connection, enumeration, and `xp_cmdshell` execution.
- `run_addcomputer`: Create computer accounts in the domain (`addcomputer.py`).
- `run_rename_machine`: Abuse sAMAccountName machine account renaming (`renameMachine.py`).
- `run_certipy`: Active Directory Certificate Services (AD CS) enumeration and escalation (`certipy`).
- `run_dnstool`: Manage AD-integrated DNS records (`dnstool.py`).
- `run_addspn`: Manage Service Principal Names on domain objects (`addspn.py`).
- `run_printerbug`: Coerce machine authentication via MS-RPRN (`printerbug.py`).

### 5. Shell & Session State (`mcp/tools/shell.py`, `mcp/tools/credentials.py`)

- `shell_exec`: Fallback arbitrary command runner with execution timeouts and output truncation.
- `credentials_add`: Thread-safe credential vault storage (username, password/hash, domain, notes).
- `credentials_get`: Query captured credentials with substring filtering.

---

## Deployment & Setup

### Prerequisites

- Docker & Docker Compose
- [ngrok](https://ngrok.com/) account for remote webhook/SSE tunneling

### 1. Environment Configuration

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` as needed:

```ini
HOST=0.0.0.0
PORT=8000
AD_STATE_DIR=./ad-pentest/state
NGROK_AUTHTOKEN=your_ngrok_token_here
NGROK_DOMAIN=your-subdomain.ngrok-free.app
```

### 2. Run with Docker Compose

The included `compose.yaml` builds and runs the container with the full offensive tooling suite and optionally creates an ngrok tunnel:

```bash
docker compose up -d
```

Check the logs:

```bash
docker compose logs -f server
```

The MCP server will be listening at `http://0.0.0.0:8000`.

### 3. Local Development (Without Docker)

Requirements: Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
# Install dependencies
uv sync

# Run the server
uv run -m adpilot_mcp
```

---

## Repository Structure

```
├── attacker-files/          # Helper payload scripts, wordlists, and webshells
│   ├── amsi-net-bypass.txt
│   ├── potential_passwords.txt
│   ├── potential_users.txt
│   ├── reverse_shell_command.py
│   ├── rockyou.txt
│   └── webshell.aspx
├── compose.yaml             # Docker Compose configuration (server + ngrok)
├── Dockerfile               # Production Ubuntu build with full pentest toolchain
├── ngrok/                   # Reverse proxy and traffic policy configuration
├── pyproject.toml           # Project metadata, dependencies, and script definitions
├── src/adpilot_mcp/
│   ├── config.py            # Pydantic Settings singleton (.env loader)
│   ├── core/
│   │   ├── executor.py      # Safe async/sync shell execution with process group management
│   │   ├── security.py      # Argument quoting, env sanitization, and safe_subpath
│   │   └── exceptions.py    # Custom exception hierarchy
│   ├── mcp/
│   │   ├── middleware.py    # ToolFilterMiddleware (phase-based tool filtering & authorization)
│   │   ├── server.py        # FastMCP factory and component registration
│   │   ├── prompts/         # MCP playbooks and methodology templates
│   │   ├── resources/       # MCP state and credential resources
│   │   └── tools/           # Modular MCP tool registrations (recon, ad_enum, kerberos, etc.)
│   ├── models/              # Pydantic data schemas (credentials, results, phases)
│   └── services/            # Offensive command builders and business logic
└── tests/                   # Unit and integration test suite
```

---

## Security & Disclaimer

> [!CAUTION]
> **Authorized Testing Only**: This software is intended strictly for authorized security assessments, penetration testing in controlled laboratory environments, and academic research. Unauthorized scanning, attacking, or interacting with networks or Active Directory domains without explicit prior consent is strictly prohibited and unlawful.
