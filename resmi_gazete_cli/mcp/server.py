from typing import Optional
from pydantic import Field

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:  # pragma: no cover
    from mcp.server.fastmcp import FastMCP as MCPServer

from resmi_gazete_cli.scraper.client import ResmiGazeteClient

mcp = MCPServer("Resmi Gazete MCP Sunucusu")


@mcp.tool()
async def get_todays_gazette() -> str:
    """
    Günün yayımlanan Resmi Gazete karar, yönetmelik, tebliğ ve ilanlarını çeker.
    Dönen metin; tarih, sayı, bölümler ve maddelerin başlıkları ile bağlantılarını içerir.
    """
    client = ResmiGazeteClient()
    gazette = await client.get_todays_gazette()
    if gazette.error:
        return f"Hata: {gazette.error}"

    lines = [f"# {gazette.tarih or 'Güncel'} Tarihli ve {gazette.sayi or '-'} Sayılı Resmî Gazete\n"]
    if gazette.mukerrer:
        lines.append(f"**Durum:** {gazette.mukerrer_no or 'Mükerrer Sayı'}\n")

    for idx, item in enumerate(gazette.items, 1):
        cat = f"[{item.kategori}] " if item.kategori else ""
        link = f" (Link: {item.link})" if item.link else ""
        lines.append(f"{idx}. {cat}{item.baslik}{link}")

    return "\n".join(lines)


@mcp.tool()
async def get_gazette_by_date(
    tarih: str = Field(..., description="Görüntülenecek gazete tarihi (GG.AA.YYYY veya YYYY-MM-DD formatında)"),
    mukerrer: Optional[int] = Field(None, description="Mükerrer sayısı (varsa, örn: 1 veya 2)")
) -> str:
    """
    Belirli bir tarihteki Resmi Gazete içeriklerini çeker.
    """
    client = ResmiGazeteClient()
    gazette = await client.get_gazette_by_date(tarih, mukerrer=mukerrer)
    if gazette.error:
        return f"Hata: {gazette.error}"

    lines = [f"# {gazette.tarih or tarih} Tarihli ve {gazette.sayi or '-'} Sayılı Resmî Gazete\n"]
    if gazette.mukerrer:
        lines.append(f"**Durum:** {gazette.mukerrer_no or 'Mükerrer Sayı'}\n")

    for idx, item in enumerate(gazette.items, 1):
        cat = f"[{item.kategori}] " if item.kategori else ""
        link = f" (Link: {item.link})" if item.link else ""
        lines.append(f"{idx}. {cat}{item.baslik}{link}")

    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
