import pytest
from unittest.mock import patch, AsyncMock
from resmi_gazete_cli.mcp.server import mcp, get_todays_gazette, get_gazette_by_date
from resmi_gazete_cli.scraper.models import DailyGazette, GazetteItem


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
