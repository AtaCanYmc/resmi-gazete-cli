import re
import pytest
from unittest.mock import patch, AsyncMock
import httpx

from resmi_gazete_cli import __version__
from resmi_gazete_cli.scraper.client import ResmiGazeteClient, normalize_iso_date


def test_package_version():
    """Paket sürümünün semver formatında olduğunu doğrular."""
    assert __version__ is not None
    assert re.match(r"^\d+\.\d+\.\d+", __version__)


def test_normalize_iso_date():
    """Farklı tarih formatlarının YYYY-MM-DD standardına dönüştürülmesi."""
    assert normalize_iso_date("18.11.2026") == "2026-11-18"
    assert normalize_iso_date("2026-11-18") == "2026-11-18"
    assert normalize_iso_date("18/11/2026") == "2026-11-18"


def test_client_initialization_default():
    """İstemcinin varsayılan parametrelerle (timeout=30, verify=True, headers) oluşturulması."""
    client = ResmiGazeteClient()
    assert client.verify is True
    assert client.timeout == 30
    assert "User-Agent" in client.headers
    assert "Accept" in client.headers
    assert client.BASE_URL == "https://resmigazete.gov.tr"


def test_client_initialization_custom():
    """İstemcinin özel parametrelerle başlatılabilmesi."""
    client = ResmiGazeteClient(timeout=10, verify=False)
    assert client.verify is False
    assert client.timeout == 10


@pytest.mark.asyncio
async def test_get_todays_gazette_success():
    """Başarılı 200 OK yanıtı durumunda istemcinin işleyişi."""
    client = ResmiGazeteClient(timeout=20, verify=True)
    html_mock = """
    <div class="row tarih">18 Kasım 2026 Tarihli ve 33434 Sayılı Resmî Gazete</div>
    <div class="html-content">
        <div class="fihrist-item"><a href="/karar.pdf">–– Test Kararı</a></div>
    </div>
    """
    mock_response = httpx.Response(
        200,
        request=httpx.Request("GET", "https://resmigazete.gov.tr"),
        text=html_mock
    )

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client_cls.return_value = mock_instance

        gazette = await client.get_todays_gazette()

        mock_client_cls.assert_called_once_with(
            timeout=20,
            headers=client.headers,
            verify=True,
            follow_redirects=True
        )
        assert gazette.error is None
        assert gazette.tarih == "18 Kasım 2026"
        assert gazette.sayi == "33434"
        assert len(gazette.items) == 1
        assert gazette.items[0].baslik == "Test Kararı"


@pytest.mark.asyncio
async def test_get_gazette_by_date_success():
    """Belirli bir tarihteki gazetenin başarıyla çekilmesi."""
    client = ResmiGazeteClient()
    html_mock = """
    <div class="preview-title">17 Kasım 2026 Tarihli ve 33433 Sayılı Resmî Gazete</div>
    <div class="html-content">
        <div class="fihrist-item"><a href="/karar.htm">–– Adli Tıp Yönetmeliği</a></div>
    </div>
    """
    mock_response = httpx.Response(
        200,
        request=httpx.Request("GET", "https://resmigazete.gov.tr/fihrist?tarih=2026-11-17"),
        text=html_mock
    )

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.get.return_value = mock_response
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client_cls.return_value = mock_instance

        gazette = await client.get_gazette_by_date("17.11.2026")

        assert gazette.error is None
        assert gazette.sayi == "33433"
        assert len(gazette.items) == 1


@pytest.mark.asyncio
async def test_get_gazette_by_date_invalid_format():
    """Geçersiz tarih girildiğinde hata mesajı döndürülmesi."""
    client = ResmiGazeteClient()
    gazette = await client.get_gazette_by_date("gecersiz.tarih.format")
    assert gazette.error is not None
    assert "Geçersiz tarih formatı" in gazette.error


@pytest.mark.asyncio
async def test_get_todays_gazette_timeout():
    """Zaman aşımı (TimeoutException) hatasının düzgün yakalanıp modellenmesi."""
    client = ResmiGazeteClient(timeout=5)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.get.side_effect = httpx.TimeoutException("Connection timed out")
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client_cls.return_value = mock_instance

        gazette = await client.get_todays_gazette()

        assert gazette.error is not None
        assert "zaman aşımına uğradı (5s)" in gazette.error


@pytest.mark.asyncio
async def test_get_todays_gazette_404_not_found():
    """404 Not Found durumunun kullanıcı dostu hata mesajına dönüştürülmesi."""
    client = ResmiGazeteClient()
    mock_request = httpx.Request("GET", "https://resmigazete.gov.tr")
    mock_response = httpx.Response(404, request=mock_request)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.get.side_effect = httpx.HTTPStatusError(
            message="Client error '404 Not Found'",
            request=mock_request,
            response=mock_response
        )
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client_cls.return_value = mock_instance

        gazette = await client.get_todays_gazette()

        assert gazette.error is not None
        assert "404 Not Found" in gazette.error


@pytest.mark.asyncio
async def test_get_todays_gazette_500_server_error():
    """500 Internal Server Error durumunun hata mesajına dönüştürülmesi."""
    client = ResmiGazeteClient()
    mock_request = httpx.Request("GET", "https://resmigazete.gov.tr")
    mock_response = httpx.Response(500, request=mock_request)

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.get.side_effect = httpx.HTTPStatusError(
            message="Server error '500 Internal Server Error'",
            request=mock_request,
            response=mock_response
        )
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client_cls.return_value = mock_instance

        gazette = await client.get_todays_gazette()

        assert gazette.error is not None
        assert "Sunucu hatası (500)" in gazette.error


@pytest.mark.asyncio
async def test_get_todays_gazette_request_error():
    """Bağlantı ve ağ hatasının (RequestError) yakalanması."""
    client = ResmiGazeteClient()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.get.side_effect = httpx.ConnectError("DNS resolution failed")
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client_cls.return_value = mock_instance

        gazette = await client.get_todays_gazette()

        assert gazette.error is not None
        assert "Bağlantı hatası oluştu" in gazette.error


@pytest.mark.asyncio
async def test_get_todays_gazette_unexpected_exception():
    """Beklenmeyen genel bir istisnanın (Exception) yakalanması."""
    client = ResmiGazeteClient()

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_instance = AsyncMock()
        mock_instance.get.side_effect = RuntimeError("Memory corruption")
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.__aexit__.return_value = None
        mock_client_cls.return_value = mock_instance

        gazette = await client.get_todays_gazette()

        assert gazette.error is not None
        assert "Beklenmeyen bir hata oluştu" in gazette.error
