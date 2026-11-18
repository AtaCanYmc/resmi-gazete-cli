from unittest.mock import patch, AsyncMock
from click.testing import CliRunner

from resmi_gazete_cli import __version__
from resmi_gazete_cli.cli.main import cli, tr_lower
from resmi_gazete_cli.scraper.models import (
    DailyGazette,
    GazetteItem,
    SearchResponse,
    SearchResultItem
)


def test_cli_version():
    """CLI sürüm parametresinin doğru çalıştığını test eder."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_help():
    """CLI yardım metninin görüntülenebildiğini test eder."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "T.C. Resmi Gazete CLI aracı" in result.output


def test_tr_lower_case_folding():
    """Türkçe İ ve I harflerinin küçük harfe doğru çevrilmesi."""
    assert tr_lower("YÖNETMELİK") == "yönetmelik"
    assert tr_lower("İLAN BÖLÜMÜ") == "ilan bölümü"
    assert tr_lower("IŞIK") == "ışık"


def test_cli_daily_command_success():
    """daily komutunun mock gazete verisiyle başarılı tablo çizimi."""
    mock_item = GazetteItem(
        tarih="18 Kasım 2026",
        sayi="33434",
        kategori="YÜRÜTME VE İDARE BÖLÜMÜ / CUMHURBAŞKANI KARARLARI",
        baslik="Örnek Karar Başlığı",
        link="https://resmigazete.gov.tr/karar.pdf"
    )
    mock_gazette = DailyGazette(
        tarih="18 Kasım 2026",
        sayi="33434",
        items=[mock_item]
    )

    with patch("resmi_gazete_cli.scraper.client.ResmiGazeteClient.get_todays_gazette", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_gazette
        runner = CliRunner()
        result = runner.invoke(cli, ["daily"])

        assert result.exit_code == 0
        assert "33434 Sayılı Resmî Gazete" in result.output
        assert "Örnek Karar" in result.output
        assert "Başlığı" in result.output


def test_cli_daily_command_json_output():
    """daily komutunun --json-output parametresi ile JSON dönmesi."""
    mock_item = GazetteItem(
        tarih="18 Kasım 2026",
        sayi="33434",
        kategori="YÖNETMELİK",
        baslik="Örnek Yönetmelik",
        link="https://resmigazete.gov.tr/yonetmelik.htm"
    )
    mock_gazette = DailyGazette(
        tarih="18 Kasım 2026",
        sayi="33434",
        items=[mock_item]
    )

    with patch("resmi_gazete_cli.scraper.client.ResmiGazeteClient.get_todays_gazette", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_gazette
        runner = CliRunner()
        result = runner.invoke(cli, ["daily", "--json-output", "-c", "Yönetmelik"])

        assert result.exit_code == 0
        assert '"total_count": 1' in result.output
        assert '"Örnek Yönetmelik"' in result.output


def test_cli_daily_command_error():
    """Hata durumunda terminale hata mesajı basılması."""
    mock_gazette = DailyGazette(error="Ağ bağlantısı koptu.")

    with patch("resmi_gazete_cli.scraper.client.ResmiGazeteClient.get_todays_gazette", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_gazette
        runner = CliRunner()
        result = runner.invoke(cli, ["daily"])

        assert result.exit_code == 0
        assert "Ağ bağlantısı koptu." in result.output


def test_cli_search_command_table():
    """search komutunun varsayılan tablo formatında çalışması."""
    mock_item = SearchResultItem(
        konu="Vergi Kanunu Kararı",
        mevzuat_adi="KANUNLAR",
        resmi_gazete_sayisi=33000,
        kanun_karar_no="7500",
        tarih="01.01.2026",
        url="https://resmigazete.gov.tr/karar.pdf"
    )
    mock_response = SearchResponse(
        total_count=1,
        page=1,
        page_size=10,
        results=[mock_item]
    )

    with patch("resmi_gazete_cli.scraper.client.ResmiGazeteClient.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_response
        runner = CliRunner(env={"COLUMNS": "160"})
        result = runner.invoke(cli, ["search", "-k", "vergi", "-t", "kanun"])

        assert result.exit_code == 0
        assert "Toplam Bulunan Kayıt: 1" in result.output
        assert "Vergi Kanunu Kararı" in result.output
        assert "KANUNLAR" in result.output


def test_cli_search_command_json_and_md():
    """search komutunun JSON ve Markdown formatlarının testi."""
    mock_item = SearchResultItem(
        konu="Tebliğ Maddesi",
        mevzuat_adi="TEBLİĞLER",
        resmi_gazete_sayisi=33001,
        kanun_karar_no="",
        tarih="02.01.2026",
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
        runner = CliRunner()

        # JSON testi
        res_json = runner.invoke(cli, ["search", "-k", "tebliğ", "-f", "json"])
        assert res_json.exit_code == 0
        assert '"total_count": 1' in res_json.output
        assert '"Tebliğ Maddesi"' in res_json.output

        # Markdown testi
        res_md = runner.invoke(cli, ["search", "-k", "tebliğ", "-f", "md"])
        assert res_md.exit_code == 0
        assert "# Resmi Gazete Arama Sonuçları" in res_md.output
        assert "| 1 | 02.01.2026 | 33001 | TEBLİĞLER |" in res_md.output
        assert "[Görüntüle](https://resmigazete.gov.tr/teblig.htm)" in res_md.output


def test_cli_search_command_error():
    """search komutunda hata döndüğünde çıktının testi."""
    mock_response = SearchResponse(error="Sunucu yanıt vermiyor")

    with patch("resmi_gazete_cli.scraper.client.ResmiGazeteClient.search", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_response
        runner = CliRunner()

        result = runner.invoke(cli, ["search", "-k", "hata"])
        assert result.exit_code == 0
        assert "Arama Hatası:" in result.output
        assert "Sunucu yanıt vermiyor" in result.output
