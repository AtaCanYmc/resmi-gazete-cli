import pytest
from unittest.mock import patch, AsyncMock
from resmi_gazete_cli.mcp.server import (
    mcp,
    get_todays_gazette,
    get_gazette_by_date,
    search_gazette
)
from resmi_gazete_cli.scraper.models import (
    DailyGazette,
    GazetteItem,
    SearchResponse,
    SearchResultItem
)


def test_mcp_server_initialization():
    """MCP sunucusunun adı ve tanımlamasının doğrulanması."""
    assert mcp.name == "Resmi Gazete MCP Sunucusu"


@pytest.mark.asyncio
async def test_mcp_get_todays_gazette_tool():
    """get_todays_gazette MCP aracının metin çıktısı üretmesi."""
    mock_item = GazetteItem(
        tarih="18 Kasım 2026",
        sayi="33434",
        kategori="CUMHURBAŞKANI KARARLARI",
        baslik="Örnek Karar",
        link="https://resmigazete.gov.tr/karar.pdf"
    )
    mock_gazette = DailyGazette(
        tarih="18 Kasım 2026",
        sayi="33434",
        items=[mock_item]
    )

    with patch("resmi_gazete_cli.scraper.client.ResmiGazeteClient.get_todays_gazette", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_gazette
        result = await get_todays_gazette()

        assert "# 18 Kasım 2026 Tarihli ve 33434 Sayılı Resmî Gazete" in result
        assert "1. [CUMHURBAŞKANI KARARLARI] Örnek Karar" in result
        assert "(Link: https://resmigazete.gov.tr/karar.pdf)" in result


@pytest.mark.asyncio
async def test_mcp_get_gazette_by_date_tool():
    """get_gazette_by_date MCP aracının çalışması."""
    mock_gazette = DailyGazette(
        tarih="17 Kasım 2026",
        sayi="33433",
        items=[]
    )

    with patch("resmi_gazete_cli.scraper.client.ResmiGazeteClient.get_gazette_by_date", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_gazette
        result = await get_gazette_by_date("17.11.2026")

        assert "# 17 Kasım 2026 Tarihli ve 33433 Sayılı Resmî Gazete" in result


@pytest.mark.asyncio
async def test_mcp_search_gazette_tool():
    """search_gazette MCP aracının çalışması ve arama sonuçlarını formatlaması."""
    mock_item = SearchResultItem(
        konu="Örnek Tebliğ",
        mevzuat_adi="TEBLİĞLER",
        resmi_gazete_sayisi=33426,
        kanun_karar_no="597",
        tarih="10.11.2026",
        url="https://resmigazete.gov.tr/teblig.htm"
    )
    mock_response = SearchResponse(
        total_count=1,
        page=1,
        page_size=10,
        results=[mock_item]
    )

    with patch("resmi_gazete_cli.scraper.client.ResmiGazeteClient.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_response
        result = await search_gazette(kelime="tebliğ", mevzuat_turu="teblig")

        assert "# Resmi Gazete Arama Sonuçları (Toplam: 1, Sayfa: 1)" in result
        assert "Örnek Tebliğ" in result
        assert "[10.11.2026]" in result
        assert "(Sayı: 33426)" in result
        assert "Link: https://resmigazete.gov.tr/teblig.htm" in result
