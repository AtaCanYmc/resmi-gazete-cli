from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Resmi Gazete MCP Sunucusu")


def main():
    mcp.run()


if __name__ == "__main__":
    main()
