try:
    from mcp.server.mcpserver import MCPServer
except ImportError:  # pragma: no cover
    from mcp.server.fastmcp import FastMCP as MCPServer

mcp = MCPServer("Resmi Gazete MCP Sunucusu")


def main():
    mcp.run()


if __name__ == "__main__":
    main()
