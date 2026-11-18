from unittest.mock import patch, AsyncMock
from click.testing import CliRunner

from resmi_gazete_cli import __version__
from resmi_gazete_cli.cli.main import cli, tr_lower
from resmi_gazete_cli.scraper.models import DailyGazette, GazetteItem


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
