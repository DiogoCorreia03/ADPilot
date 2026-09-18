import asyncio
import os
import sys
from typing import Any

from dotenv import find_dotenv, load_dotenv
from rich.prompt import Confirm, Prompt
from adpilot_agent.util import get_settings, mcp_tool_session

# Ensure local .env or current working directory .env is loaded
load_dotenv(find_dotenv(usecwd=True))


def get_pentest_phase(settings: Any = None) -> str | None:
    """Retrieve the pentest_phase from settings or environment variables."""
    phase = getattr(settings, "PENTEST_PHASE", None) if settings is not None else None
    if isinstance(phase, str) and phase.strip():
        return phase.strip()

    env_phase = os.getenv("PENTEST_PHASE") or os.getenv("pentest_phase")
    if env_phase and env_phase.strip():
        return env_phase.strip()

    return None

from .runner import execute_tool
from .schema_parser import (
    cast_parameter_value,
    get_tool_schema,
    parse_tool_parameters,
)
from .ui import (
    console,
    display_args_preview,
    display_execution_result,
    display_tool_details,
    display_tools_table,
    print_banner,
    prompt_help,
)


def collect_tool_arguments(tool: Any) -> dict[str, Any] | None:
    """Interactively prompt the user for tool arguments guided by the tool's schema.

    Returns:
        dict[str, Any] | None: Collected arguments dict, or None if user canceled.
    """
    schema = get_tool_schema(tool)
    params = parse_tool_parameters(schema)

    if not params:
        console.print("[italic green]This tool requires no arguments.[/italic green]")
        return {}

    display_tool_details(tool)
    console.print("[dim]Enter argument values. Type ':cancel' to abort, ':skip' to leave optional field empty.[/dim]\n")

    arguments: dict[str, Any] = {}

    for param in params:
        while True:
            # Build prompt label
            badge = "[bold red]* REQUIRED[/bold red]" if param.is_required else "[dim]optional[/dim]"
            default_hint = f" [default: {param.default}]" if param.default is not None else ""
            type_hint = f"({param.type_display})"

            console.print(f"[bold cyan]{param.name}[/bold cyan] {type_hint} - {badge}{default_hint}")
            if param.description:
                console.print(f"  [dim]{param.description}[/dim]")

            # Display enum options if present
            if param.enum_values:
                enum_options = "  Allowed choices:\n" + "\n".join(
                    f"    [{i}] {val}" for i, val in enumerate(param.enum_values, 1)
                )
                console.print(f"[dim]{enum_options}[/dim]")

            default_val_str = str(param.default) if param.default is not None else None

            try:
                user_val = Prompt.ask(f"  Enter {param.name}", default=default_val_str)
            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Argument entry aborted.[/yellow]")
                return None

            cleaned = user_val.strip() if user_val else ""

            if cleaned.lower() in (":cancel", ":abort"):
                console.print("[yellow]Cancelled by user.[/yellow]")
                return None

            if cleaned.lower() == ":skip":
                if param.is_required and param.default is None:
                    console.print("[red]Cannot skip a required parameter without a default.[/red]\n")
                    continue
                # Skip and omit or set None
                if param.default is not None:
                    arguments[param.name] = param.default
                break

            cast_val, error = cast_parameter_value(param, cleaned)
            if error:
                console.print(f"[bold red]Error:[/bold red] {error}\n")
                continue

            # Store argument (omit if None and not required)
            if cast_val is not None or param.is_required:
                arguments[param.name] = cast_val
            break

        console.print()

    return arguments


def find_tool(tools: list[Any], query: str) -> Any | None:
    """Find a tool by 1-based index or by exact/prefix name."""
    query_clean = query.strip()

    # Index lookup
    if query_clean.isdigit():
        idx = int(query_clean) - 1
        if 0 <= idx < len(tools):
            return tools[idx]
        return None

    # Exact name match
    exact_matches = [t for t in tools if getattr(t, "name", "").lower() == query_clean.lower()]
    if len(exact_matches) == 1:
        return exact_matches[0]

    # Prefix / substring matches
    sub_matches = [t for t in tools if query_clean.lower() in getattr(t, "name", "").lower()]
    if len(sub_matches) == 1:
        return sub_matches[0]
    elif len(sub_matches) > 1:
        console.print(f"[yellow]Multiple tools matched '{query_clean}': {', '.join(t.name for t in sub_matches)}[/yellow]")
        return None

    return None


async def run_interactive_session():
    """Main interactive loop keeping the MCP tool session alive."""
    settings = get_settings()
    pentest_phase = get_pentest_phase(settings)
    extra_headers = {"pentest_phase": pentest_phase} if pentest_phase else None

    print_banner(
        server_url=str(settings.ATTACKER_MACHINE_URL),
        network=settings.NETWORK,
        dc_ip=settings.DC_IP,
        pentest_phase=pentest_phase or "",
    )

    running = True
    while running:
        extra_headers = {"pentest_phase": pentest_phase} if pentest_phase else None

        if pentest_phase:
            console.print(
                f"[dim]Connecting to MCP Server with pentest phase: [bold magenta]{pentest_phase}[/bold magenta]...[/dim]"
            )
        else:
            console.print("[dim]Connecting to MCP Server...[/dim]")

        try:
            async with mcp_tool_session(
                limit_scope_label="InteractiveCLI",
                extra_headers=extra_headers,
                phase=pentest_phase,
            ) as tools:
                console.print(f"[bold green]Connected successfully![/bold green] Loaded [bold cyan]{len(tools)}[/bold cyan] tools.\n")
                display_tools_table(tools)
                prompt_help()

                current_filter: str | None = None

                while True:
                    try:
                        cmd = Prompt.ask("[bold magenta]mcp>[/bold magenta]")
                    except (KeyboardInterrupt, EOFError):
                        console.print("\n[yellow]Exiting MCP CLI...[/yellow]")
                        running = False
                        break

                    cmd_clean = cmd.strip()
                    if not cmd_clean:
                        continue

                    cmd_lower = cmd_clean.lower()

                    # Builtin navigation commands
                    if cmd_lower in ("exit", "quit", "q"):
                        console.print("[green]Goodbye![/green]")
                        running = False
                        break

                    if cmd_lower in ("help", "?"):
                        prompt_help()
                        continue

                    if cmd_lower == "clear":
                        os.system("clear" if os.name != "nt" else "cls")
                        print_banner(
                            server_url=str(settings.ATTACKER_MACHINE_URL),
                            network=settings.NETWORK,
                            dc_ip=settings.DC_IP,
                            pentest_phase=pentest_phase or "",
                        )
                        continue

                    if cmd_lower in ("list", "ls"):
                        current_filter = None
                        display_tools_table(tools)
                        continue

                    if cmd_lower.startswith("search ") or cmd_lower.startswith("filter "):
                        _, term = cmd_clean.split(" ", 1)
                        current_filter = term.strip()
                        display_tools_table(tools, filter_query=current_filter)
                        continue

                    if cmd_lower.startswith("info "):
                        _, target = cmd_clean.split(" ", 1)
                        target_tool = find_tool(tools, target)
                        if target_tool:
                            display_tool_details(target_tool)
                        else:
                            console.print(f"[red]Tool '{target}' not found.[/red]")
                        continue

                    if cmd_lower == "phase":
                        if pentest_phase:
                            console.print(f"[bold cyan]Current pentest phase:[/bold cyan] [bold magenta]{pentest_phase}[/bold magenta]\n")
                        else:
                            console.print("[yellow]No pentest phase currently set. Use 'phase <name>' to set one.[/yellow]\n")
                        continue

                    if cmd_lower.startswith("phase "):
                        _, new_phase = cmd_clean.split(" ", 1)
                        new_phase = new_phase.strip()
                        if new_phase.lower() in ("none", "clear", "reset", "off", "unset", "-"):
                            if pentest_phase is None:
                                console.print("[yellow]Pentest phase is already unset.[/yellow]\n")
                                continue
                            pentest_phase = None
                            console.print("[yellow]Resetting pentest phase (removing header). Reconnecting to MCP server...[/yellow]\n")
                        else:
                            if pentest_phase == new_phase:
                                console.print(f"[yellow]Pentest phase is already '{new_phase}'. Reconnecting to MCP server...[/yellow]\n")
                            else:
                                pentest_phase = new_phase
                                console.print(f"[green]Switching pentest phase to [bold magenta]{new_phase}[/bold magenta]. Reconnecting to MCP server...[/green]\n")
                        break

                    if cmd_lower == "reconnect":
                        console.print("[cyan]Reconnecting to MCP server...[/cyan]\n")
                        break

                    # Tool selection by index or name
                    selected_tool = find_tool(tools, cmd_clean)
                    if selected_tool is None:
                        console.print(f"[red]Unknown command or tool: '{cmd_clean}'. Type 'help' for commands or 'list' for tools.[/red]")
                        continue

                    # Collect arguments and execute
                    while True:
                        args = collect_tool_arguments(selected_tool)
                        if args is None:
                            break

                        display_args_preview(selected_tool.name, args)

                        confirmed = Confirm.ask(f"Execute [bold cyan]{selected_tool.name}[/bold cyan]?", default=True)
                        if not confirmed:
                            console.print("[yellow]Execution cancelled.[/yellow]")
                            break

                        console.print(f"\n[dim]Executing {selected_tool.name}...[/dim]")
                        result = await execute_tool(selected_tool, args)
                        display_execution_result(result)

                        repeat = Confirm.ask(f"\nRe-run [bold cyan]{selected_tool.name}[/bold cyan] with new parameters?", default=False)
                        if not repeat:
                            break

        except Exception as e:
            console.print(f"\n[bold red]MCP Session Error:[/bold red] {e}")
            console.print("[yellow]Please check your network connection and credentials in .env.[/yellow]")
            break


def main():
    """CLI entrypoint."""
    try:
        asyncio.run(run_interactive_session())
    except KeyboardInterrupt:
        console.print("\n[yellow]Session aborted by user.[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    main()
