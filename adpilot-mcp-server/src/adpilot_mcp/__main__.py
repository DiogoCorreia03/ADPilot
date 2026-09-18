import logging
from adpilot_mcp.config import get_settings
from adpilot_mcp.core.executor import run_command
from adpilot_mcp.mcp.server import create_server

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main() -> None:
    settings = get_settings()
    logger.info("Starting ADPilot MCP server...")
    try:
        # Setup nxc for first time use to avoid output clutter on first use
        run_command("nxc")
        mcp = create_server()
        mcp.run(
            transport="streamable-http",
            show_banner=False,
            host=settings.host,
            port=settings.port,
        )
    except KeyboardInterrupt:
        logger.info("Shutting down server (Ctrl+C)...")
    except Exception as e:
        logger.error(f"Server error: {e}")
        logger.info("Shutting down server due to previous error...")
    finally:
        logger.info("Server stopped.")


if __name__ == "__main__":
    main()
