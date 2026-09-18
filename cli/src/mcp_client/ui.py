import json
from typing import Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from rich.text import Text

from .runner import ToolExecutionResult
from .schema_parser import parse_tool_parameters, get_tool_schema

console = Console()


def print_banner(
    server_url: str = "",
    network: str = "",
    dc_ip: str = "",
    pentest_phase: str = "",
):
    """Display the application header with connection and environment information."""
    banner_text = Text()
    banner_text.append("MCP Interactive Tool CLI\n", style="bold cyan")
    banner_text.append("Active Directory Pentesting & Operations Client\n\n", style="italic dim")
    if server_url:
        banner_text.append("MCP Server: ", style="bold")
        banner_text.append(f"{server_url}\n", style="green")
    if network:
        banner_text.append("Target Subnet: ", style="bold")
        banner_text.append(f"{network}  |  ", style="yellow")
    if dc_ip:
        banner_text.append("DC IP: ", style="bold")
        banner_text.append(f"{dc_ip}\n", style="yellow")
    if pentest_phase:
        banner_text.append("Pentest Phase: ", style="bold")
        banner_text.append(f"{pentest_phase}\n", style="magenta")

    console.print(Panel(banner_text, border_style="cyan", padding=(0, 2)))


def display_tools_table(tools: list[Any], filter_query: str | None = None):
    """Render a clean, formatted table of available tools."""
    table = Table(title="Available MCP Tools", title_style="bold magenta", border_style="dim")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Tool Name", style="bold green")
    table.add_column("Description", style="white")
    table.add_column("Required Args", style="yellow")

    matched_count = 0
    query = filter_query.lower().strip() if filter_query else None

    for idx, tool in enumerate(tools, start=1):
        name = getattr(tool, "name", "unknown")
        desc = getattr(tool, "description", "") or ""
        # Truncate first line for clean table
        desc_summary = desc.strip().split("\n")[0]
        if len(desc_summary) > 80:
            desc_summary = desc_summary[:77] + "..."

        if query and query not in name.lower() and query not in desc.lower():
            continue

        schema = get_tool_schema(tool)
        params = parse_tool_parameters(schema)
        req_params = [p.name for p in params if p.is_required]
        req_display = ", ".join(req_params) if req_params else "[dim]none[/dim]"

        table.add_row(str(idx), name, desc_summary, req_display)
        matched_count += 1

    if matched_count == 0:
        if query:
            console.print(f"[yellow]No tools matched filter: '{filter_query}'[/yellow]")
        else:
            console.print("[yellow]No tools available from the MCP server.[/yellow]")
        return

    console.print(table)
    console.print(f"[dim]Showing {matched_count} of {len(tools)} tool(s)[/dim]\n")


def display_tool_details(tool: Any):
    """Render full schema documentation for a selected tool."""
    name = getattr(tool, "name", "unknown")
    desc = getattr(tool, "description", "No description provided.")
    schema = get_tool_schema(tool)
    params = parse_tool_parameters(schema)

    console.print(f"\n[bold green]Tool:[/bold green] [bold white]{name}[/bold white]")
    console.print(Panel(desc.strip(), title="Description", title_align="left", border_style="dim"))

    if not params:
        console.print("[italic dim]This tool takes no arguments.[/italic dim]\n")
        return

    table = Table(title=f"Arguments for {name}", title_style="bold cyan", border_style="dim")
    table.add_column("Parameter", style="bold cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Required", justify="center")
    table.add_column("Default", style="dim")
    table.add_column("Description", style="white")

    for p in params:
        req_badge = "[bold red]YES[/bold red]" if p.is_required else "[dim]no[/dim]"
        default_str = str(p.default) if p.default is not None else "[dim]None[/dim]"
        if p.enum_values:
            enum_str = f"\n[dim]Choices: {', '.join(str(v) for v in p.enum_values)}[/dim]"
        else:
            enum_str = ""
        table.add_row(p.name, p.type_display, req_badge, default_str, p.description + enum_str)

    console.print(table)
    console.print()


def display_args_preview(tool_name: str, arguments: dict[str, Any]):
    """Display arguments configured for execution before confirming."""
    table = Table(title=f"Execution Plan: {tool_name}", title_style="bold yellow", border_style="dim")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")

    for k, v in arguments.items():
        if isinstance(v, (dict, list)):
            val_display = json.dumps(v)
        elif v is None:
            val_display = "[dim italic]null[/dim italic]"
        else:
            val_display = str(v)
        table.add_row(k, val_display)

    console.print(table)


def display_execution_result(result: ToolExecutionResult):
    """Render the tool's execution result in a clean, informative layout."""
    console.print()
    elapsed_str = f" in {result.elapsed_seconds:.2f}s" if result.elapsed_seconds else ""

    # Status header
    if result.success:
        code_str = f" (exit code {result.returncode})" if result.returncode is not None else ""
        console.print(Panel(f"[bold green]✔ TOOL EXECUTION SUCCEEDED{code_str}{elapsed_str}[/bold green]", border_style="green"))
    else:
        code_str = f" (exit code {result.returncode})" if result.returncode is not None else ""
        console.print(Panel(f"[bold red]✖ TOOL EXECUTION FAILED{code_str}{elapsed_str}[/bold red]", border_style="red"))

    # Command panel
    if result.command:
        syntax = Syntax(result.command, "bash", theme="monokai", word_wrap=True)
        console.print(Panel(syntax, title="[bold cyan]Executed Command[/bold cyan]", title_align="left", border_style="cyan"))

    # Stdout panel
    if result.stdout:
        console.print(Panel(result.stdout.strip(), title="[bold green]Standard Output (stdout)[/bold green]", title_align="left", border_style="green"))
    elif not result.stderr:
        console.print(Panel("[dim italic]No standard output produced.[/dim italic]", title="Standard Output", border_style="dim"))

    # Stderr panel
    if result.stderr and result.stderr.strip():
        console.print(Panel(result.stderr.strip(), title="[bold red]Standard Error (stderr)[/bold red]", title_align="left", border_style="red"))

    # If raw non-JSON was returned and not yet printed
    if not result.is_json and not result.stdout and result.raw_output:
        console.print(Panel(result.raw_output.strip(), title="Raw Result", border_style="dim"))


def prompt_help():
    """Display interactive commands help."""
    table = Table(title="Interactive Commands", title_style="bold yellow", border_style="dim")
    table.add_column("Command", style="bold cyan")
    table.add_column("Description", style="white")

    table.add_row("<number>", "Select tool by index number (e.g. 1, 5, 12)")
    table.add_row("<tool_name>", "Select tool by exact name or unique prefix (e.g. run_dnstool)")
    table.add_row("search <term>", "Filter tool list by name or description (e.g. search kerberos)")
    table.add_row("list / ls", "Reset filter and display all tools")
    table.add_row("info <tool>", "Show schema and parameters without running")
    table.add_row("phase [name]", "Show or set pentest phase and reconnect (e.g. phase shell_only, phase none)")
    table.add_row("reconnect", "Reconnect to MCP server and refresh tools")
    table.add_row("clear", "Clear terminal screen")
    table.add_row("exit / quit / q", "Exit the program")

    console.print(table)
    console.print("[dim]During argument entry: type ':cancel' to abort, ':skip' to leave optional field empty.[/dim]\n")
