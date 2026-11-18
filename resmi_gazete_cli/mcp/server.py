from typing import Optional

try:
    from mcp.server.mcpserver import MCPServer
except ImportError:  # pragma: no cover
    from mcp.server.fastmcp import FastMCP as MCPServer

from resmi_gazete_cli.scraper.client import ResmiGazeteClient
from resmi_gazete_cli.scraper.models import SearchCriteria

mcp = MCPServer("Resmi Gazete MCP Sunucusu")

MEVZUAT_ALIASES = {
    "anayasa": "0010.02",
    "kanun": "0010",
    "kanunlar": "0010",
    "kararname": "0010.03",
    "cb-kararname": "0010.03",
    "cb-karar": "0010.04",
    "cumhurbaskani-karari": "0010.04",
    "yonetmelik": "0450.01",
    "yonetmelikler": "0450.01",
    "teblig": "0500",
    "tebligler": "0500",
    "genelge": "0490",
    "genelgeler": "0490",
    "aym": "0540",
    "anayasa-mahkemesi": "0540",
    "yargitay": "0550",
    "danistay": "0560",
    "sayistay": "0610",
    "atama": "0280",
}


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
    tarih: str,
    mukerrer: Optional[int] = None
) -> str:
    """
    Belirli bir tarihteki Resmi Gazete içeriklerini çeker.
    tarih: GG.AA.YYYY veya YYYY-MM-DD
    mukerrer: Mükerrer sayısı (varsa, örn: 1 veya 2)
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


@mcp.tool()
async def search_gazette(
    kelime: str = "",
    baslangic_tarihi: str = "",
    bitis_tarihi: str = "",
    sayi: str = "",
    mevzuat_sayisi: str = "",
    mevzuat_turu: str = "",
    mukerrer: str = "",
    page: int = 1,
    page_size: int = 10
) -> str:
    """
    Resmi Gazete arama sisteminde (/Home/Filter) detaylı filtreleme yapar.
    kelime: Aranacak kelime veya kelime öbeği
    baslangic_tarihi: Başlangıç Tarihi (GG.AA.YYYY veya YYYY-MM-DD)
    bitis_tarihi: Bitiş Tarihi (GG.AA.YYYY veya YYYY-MM-DD)
    sayi: Resmi Gazete sayısı
    mevzuat_sayisi: Kanun veya Karar numarası
    mevzuat_turu: Mevzuat türü kodu veya takma adı (kanun, teblig, yonetmelik vb.)
    mukerrer: Mükerrer durumu ('', 'HAYIR', 'EVET', '1', '2')
    """
    resolved_tur = MEVZUAT_ALIASES.get(mevzuat_turu.lower().strip(), mevzuat_turu.strip())
    criteria = SearchCriteria(
        kelime=kelime,
        baslangic_tarihi=baslangic_tarihi,
        bitis_tarihi=bitis_tarihi,
        sayi=sayi,
        mevzuat_sayisi=mevzuat_sayisi,
        mevzuat_turu=resolved_tur,
        mukerrer=mukerrer,
        page=page,
        page_size=page_size
    )

    client = ResmiGazeteClient()
    response = await client.search(criteria)

    if response.error:
        return f"Arama Hatası: {response.error}"

    lines = [f"# Resmi Gazete Arama Sonuçları (Toplam: {response.total_count}, Sayfa: {response.page})\n"]
    if not response.results:
        lines.append("Arama kriterlerine uygun sonuç bulunamadı.")
        return "\n".join(lines)

    start_idx = (response.page - 1) * response.page_size
    for idx, item in enumerate(response.results, start=start_idx + 1):
        tarih = f"[{item.tarih}]" if item.tarih else ""
        sayi_str = f"(Sayı: {item.resmi_gazete_sayisi})" if item.resmi_gazete_sayisi else ""
        tur = f"({item.mevzuat_adi})" if item.mevzuat_adi else ""
        no_str = f"No: {item.kanun_karar_no}" if item.kanun_karar_no else ""
        link_str = f"Link: {item.url}" if item.url else ""

        meta = " - ".join([p for p in [tarih, sayi_str, tur, no_str] if p])
        lines.append(f"{idx}. {meta}\n   {item.konu}\n   {link_str}")

    return "\n".join(lines)


@mcp.tool()
async def get_document_content(url: str) -> str:
    """
    Resmi Gazete karar veya yönetmelik dokümanının metin içeriğini çeker.
    url: Dokümanın bağlantı adresi (HTM veya PDF)
    """
    client = ResmiGazeteClient()
    doc = await client.get_document_content(url)

    if doc.error:
        return f"Doküman Hatası: {doc.error}"

    header = f"# Doküman İçeriği: {doc.url}\nTür: {doc.content_type}\n\n"
    return header + doc.icerik


def main():
    mcp.run()


if __name__ == "__main__":
    main()
