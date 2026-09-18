from typing import Literal
from fastmcp import FastMCP
from adpilot_mcp.models.phases import PentestPhase
from adpilot_mcp.services import recon as recon_service


def register(mcp: FastMCP) -> None:
    @mcp.tool(tags={PentestPhase.EXTERNAL_RECONNAISSANCE})
    async def run_curl(
        url: str,
        method: str = "GET",
        headers: str | None = None,
        data: str | None = None,
        extra_args: str | None = None,
        timeout: int = 60,
    ) -> str:
        """
        Run a curl command against a URL.

        :param url: The URL to request.
        :param method: The HTTP method to use (default is "GET").
        :param headers: The headers to include in the request.
        :param data: The data to include in the request body.
        :param extra_args: Additional arguments for curl.
        :param timeout: Maximum time in seconds that the command is allowed to run for (default is 60 seconds).
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await recon_service.run_curl(
            url=url,
            method=method,
            headers=headers,
            data=data,
            extra_args=extra_args,
            timeout=timeout,
        )
        return result.to_mcp_result()

    @mcp.tool(
        tags={
            PentestPhase.EXTERNAL_RECONNAISSANCE,
            PentestPhase.INTERNAL_RECONNAISSANCE,
        }
    )
    async def run_nmap_scan(
        target: str, flags: str = "-sV --open -T4", timeout: int = 300
    ) -> str:
        """
        Run a Nmap scan on a target or range with optional flags. Returns raw output.

        :param target: The target IP address, CIDR or hostname.
        :param flags: Additional arguments for Nmap (default is "-sV --open -T4", use "-h" for help).
        :param timeout: Maximum time in seconds that the command is allowed to run for (default is 300 seconds).
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await recon_service.run_nmap_scan(
            target=target, flags=flags, timeout=timeout
        )
        return result.to_mcp_result()

    @mcp.tool(
        tags={
            PentestPhase.EXTERNAL_RECONNAISSANCE,
            PentestPhase.INTERNAL_RECONNAISSANCE,
        }
    )
    async def run_nslookup(
        query: str,
        record_type: Literal["A", "AAAA", "MX", "NS", "SRV", "TXT", "PTR"]
        | None = None,
        extra_args: str | None = None,
        timeout: int = 60,
    ) -> str:
        """
        Run nslookup to query DNS records.

        :param query: The domain name or IP address to query.
        :param record_type: DNS record type (e.g., 'A', 'AAAA', 'MX', 'NS', 'SRV', 'TXT', 'PTR').
        :param timeout: Maximum execution time in seconds.
        :param extra_args: Additional arguments for nslookup. (e.g. '_ldap._tcp.dc._msdcs.corp.local' or '_kerberos._tcp.dc._msdcs.corp.local')
        :return: A dictionary containing stdout, stderr and returncode.
        """
        result = await recon_service.run_nslookup(
            query=query, record_type=record_type, extra_args=extra_args, timeout=timeout
        )
        return result.to_mcp_result()
