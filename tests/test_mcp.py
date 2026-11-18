from resmi_gazete_cli.mcp.server import mcp


def test_mcp_server_initialization():
    """MCP sunucusunun adı ve tanımlamasının doğrulanması."""
    assert mcp.name == "Resmi Gazete MCP Sunucusu"
