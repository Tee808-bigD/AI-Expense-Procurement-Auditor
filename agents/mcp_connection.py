"""
agents/mcp_connection.py
--------------------------
Builds the McpToolset connection that agents use to reach the MCP server
defined in mcp_server/server.py.

Uses a stdio transport: ADK spawns the MCP server as a subprocess and
talks to it over stdin/stdout. This keeps the demo self-contained (no
network ports to manage) while still being a real MCP client/server
relationship -- not a direct function call.
"""

import sys
from pathlib import Path

from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from mcp import StdioServerParameters

MCP_SERVER_PATH = Path(__file__).parent.parent / "mcp_server" / "server.py"


def build_expense_mcp_toolset(tool_filter: list[str] | None = None) -> McpToolset:
    """Create an McpToolset connected to the local expense ledger MCP server.

    Args:
        tool_filter: Optional list of tool names to expose to a given agent.
            Use this to give each agent the minimum tools it needs
            (least-privilege), e.g. the Ingestion Agent only needs
            ['get_expenses'], not the write tools.

    Returns:
        A configured McpToolset instance.
    """
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[str(MCP_SERVER_PATH)],
            ),
            timeout=10.0,
        ),
        tool_filter=tool_filter,
    )
