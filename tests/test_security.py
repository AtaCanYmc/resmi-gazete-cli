import pytest
from unittest.mock import patch, AsyncMock
import httpx

from click.testing import CliRunner
from resmi_gazete_cli.cli.main import cli
from resmi_gazete_cli.scraper.client import ResmiGazeteClient
from resmi_gazete_cli.scraper.models import SearchCriteria
from resmi_gazete_cli.scraper.security import (
    is_safe_url,
    validate_target_url,
    SSRFError,
)


def test_is_safe_url_allowed_domains():
    """Güvenli ve izin verilen alan adlarının başarıyla onaylanması."""
    assert is_safe_url("https://resmigazete.gov.tr/fihrist") is True
    assert is_safe_url("https://www.resmigazete.gov.tr/eskiler/2026/11/20261118-1.htm") is True
    assert is_safe_url("http://resmigazete.gov.tr/ilan") is True
    assert is_safe_url("https://mevzuat.gov.tr/mevzuatMetin/1.5.7524.pdf") is True


def test_is_safe_url_blocked_schemes():
    """file, ftp, javascript vb. güvensiz URL şemalarının engellenmesi."""
    assert is_safe_url("file:///etc/passwd") is False
    assert is_safe_url("javascript:alert(1)") is False
    assert is_safe_url("data:text/html;base64,PHNjcmlwdD4=") is False
    assert is_safe_url("ftp://resmigazete.gov.tr/file.txt") is False
    assert is_safe_url("") is False
    assert is_safe_url("not_a_url") is False


def test_is_safe_url_ssrf_and_private_ips():
    """Özel ağ, loopback ve bulut metadata IP adreslerinin (SSRF) engellenmesi."""
    assert is_safe_url("http://127.0.0.1/admin") is False
    assert is_safe_url("http://localhost:8080/metrics") is False
    assert is_safe_url("http://169.254.169.254/latest/meta-data") is False
    assert is_safe_url("http://10.0.0.1/internal") is False
    assert is_safe_url("http://192.168.1.1/router") is False
    assert is_safe_url("http://172.16.0.1/secret") is False
    assert is_safe_url("http://[::1]/internal") is False


def test_is_safe_url_blocked_external_domains():
    """İzin listesinde bulunmayan harici alan adlarının engellenmesi."""
    assert is_safe_url("https://attacker-controlled.com/malicious.htm") is False
    assert is_safe_url("https://google.com") is False
    assert is_safe_url("https://resmigazete.gov.tr.attacker.com") is False


def test_is_safe_url_blocked_nonstandard_ports():
    """Standart dışı portlara erişimin engellenmesi."""
    assert is_safe_url("https://resmigazete.gov.tr:8080/test") is False
    assert is_safe_url("http://resmigazete.gov.tr:22/ssh") is False


def test_validate_target_url():
    """validate_target_url fonksiyonunun geçerli ve geçersiz URL davranışları."""
    safe = validate_target_url("https://resmigazete.gov.tr/fihrist")
    assert safe == "https://resmigazete.gov.tr/fihrist"

    with pytest.raises(SSRFError) as exc_info:
        validate_target_url("http://169.254.169.254/metadata")
    assert "İzin verilmeyen veya güvensiz hedef URL" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_document_content_ssrf_protection():
    """get_document_content metodunun harici/iç IP adreslerine SSRF isteklerini engellemesi."""
    client = ResmiGazeteClient()
    doc = await client.get_document_content("http://169.254.169.254/latest/meta-data/")
    assert doc.error is not None
    assert "Güvenlik hatası" in doc.error
    assert "İzin verilmeyen veya güvensiz URL" in doc.error


@pytest.mark.asyncio
async def test_get_document_content_redirect_to_ssrf_blocked():
    """resmigazete.gov.tr üzerinden iç ağa yönlendirme (Open Redirect SSRF) girişiminin engellenmesi."""
    client = ResmiGazeteClient()

    initial_request = httpx.Request("GET", "https://resmigazete.gov.tr/redirect-target")
    redirect_request = httpx.Request("GET", "http://127.0.0.1:8080/internal")

    resp1 = httpx.Response(302, request=initial_request, headers={"location": "http://127.0.0.1:8080/internal"})
    resp2 = httpx.Response(200, request=redirect_request, text="<html><body>Internal secret</body></html>")
    resp2.history = [resp1]

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = resp2
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client_cls.return_value = mock_instance

        doc = await client.get_document_content("https://resmigazete.gov.tr/redirect-target")
        assert doc.error is not None
        assert "Güvenlik hatası" in doc.error


@pytest.mark.asyncio
async def test_response_too_large_dos_protection():
    """Maksimum boyuttan (10 MB) büyük yanıtların DoS korumasıyla engellenmesi."""
    client = ResmiGazeteClient(max_response_size=1024)  # Test için 1 KB sınır

    huge_payload = b"A" * 2048
    mock_resp = httpx.Response(
        200,
        request=httpx.Request("GET", "https://resmigazete.gov.tr/eskiler/test.htm"),
        content=huge_payload
    )

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_resp
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client_cls.return_value = mock_instance

        doc = await client.get_document_content("https://resmigazete.gov.tr/eskiler/test.htm")
        assert doc.error is not None
        assert "Güvenlik hatası" in doc.error
        assert "izin verilen sınırı aştı" in doc.error


def test_cli_rich_markup_injection_protection():
    """Terminalde Rich markup karakterleri içeren başlıkların güvenle işlenmesi."""
    runner = CliRunner(env={"COLUMNS": "160"})
    malicious_item = {
        "tarih": "18.11.2026",
        "sayi": "33434",
        "mukerrer": False,
        "mukerrer_no": None,
        "items": [
            {
                "tarih": "18.11.2026",
                "sayi": "33434",
                "bolum": "[bold red]Yürütme[/bold red]",
                "alt_kategori": "Karar",
                "kategori": "[bold]Kategori[/bold]",
                "baslik": "[link=http://evil.com]Phishing Başlık[/link] [Dengesiz Köşeli Parantez",
                "link": "https://resmigazete.gov.tr/test.htm"
            }
        ]
    }

    with patch("resmi_gazete_cli.scraper.client.ResmiGazeteClient.get_todays_gazette") as mock_daily:
        from resmi_gazete_cli.scraper.models import DailyGazette
        mock_daily.return_value = DailyGazette(**malicious_item)

        result = runner.invoke(cli, ["daily"])
        assert result.exit_code == 0
        assert "Phishing Başlık" in result.output


def test_search_criteria_length_validation():
    """SearchCriteria modelinde çok uzun dizgelerin sınırlandırılması."""
    criteria = SearchCriteria(
        kelime="A" * 200,
        sayi="12345"
    )
    assert len(criteria.kelime) == 200

    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        SearchCriteria(kelime="A" * 251)

    with pytest.raises(ValidationError):
        SearchCriteria(sayi="1" * 51)
