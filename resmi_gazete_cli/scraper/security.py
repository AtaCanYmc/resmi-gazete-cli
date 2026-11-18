import ipaddress
from typing import Optional, Set
from urllib.parse import urlparse
import httpx

# Güvenli varsayılan: Yalnızca T.C. Resmi Gazete ve ilişkili kamu mevzuat alan adları
DEFAULT_ALLOWED_DOMAINS: Set[str] = {
    "resmigazete.gov.tr",
    "www.resmigazete.gov.tr",
    "mevzuat.gov.tr",
    "www.mevzuat.gov.tr",
}

# Bellek ve DoS koruması: Maksimum yanıt boyutu (10 MB)
MAX_RESPONSE_SIZE: int = 10 * 1024 * 1024


class SecurityError(Exception):
    """Güvenlik denetimi ihlali genel istisnası."""
    pass


class SSRFError(SecurityError):
    """İzin verilmeyen ana makine veya SSRF girişimlerinde fırlatılır."""
    pass


class ResponseTooLargeError(SecurityError):
    """Sunucu yanıtı izin verilen maksimum boyutu aştığında fırlatılır."""
    pass


def _is_safe_ip(hostname: str) -> bool:
    """Hostname bir IP adresi ise özel/loopback/link-local olup olmadığını kontrol eder."""
    try:
        ipaddress.ip_address(hostname)
        return False
    except ValueError:
        return True


def _is_allowed_domain(hostname: str, allowed: Set[str]) -> bool:
    """Hostname'in izin verilen alan adı veya alt alan adı olup olmadığını doğrular."""
    for allowed_domain in allowed:
        allowed_domain = allowed_domain.lower()
        if hostname == allowed_domain or hostname.endswith("." + allowed_domain):
            return True
    return False


def is_safe_url(url: str, allowed_domains: Optional[Set[str]] = None) -> bool:
    """
    Verilen URL'nin şema, alan adı ve IP kısıtlamalarına uygunluğunu denetler.

    Kurallar:
    1. Yalnızca 'http' ve 'https' şemalarına izin verilir.
    2. Ana makine (hostname) boş olamaz.
    3. Özel/yerel IP adreslerine (localhost, 127.0.0.1, 10.0.0.0/8, 192.168.0.0/16,
       172.16.0.0/12, 169.254.169.254, ::1 vb.) erişim kesinlikle engellenir.
    4. Yalnızca izin verilen alan adlarına (veya alt alan adlarına) erişilebilir.
    5. Özel portlara (80 ve 443 dışı) izin verilmez.
    """
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url.strip())
    except Exception:
        return False

    if parsed.scheme.lower() not in ("http", "https"):
        return False

    hostname = parsed.hostname
    if not hostname:
        return False
    hostname = hostname.lower()

    if not _is_safe_ip(hostname):
        return False

    if parsed.port and parsed.port not in (80, 443):
        return False

    allowed = allowed_domains if allowed_domains is not None else DEFAULT_ALLOWED_DOMAINS
    return _is_allowed_domain(hostname, allowed)


def validate_target_url(url: str, allowed_domains: Optional[Set[str]] = None) -> str:
    """
    URL'yi doğrular; güvenli değilse SSRFError fırlatır, güvenliyse temizlenmiş URL döner.
    """
    clean_url = url.strip()
    if not is_safe_url(clean_url, allowed_domains=allowed_domains):
        raise SSRFError(
            f"Güvenlik Uyarısı: İzin verilmeyen veya güvensiz hedef URL engellendi: '{clean_url}'"
        )
    return clean_url


async def safe_read_response(response: httpx.Response, max_size: int = MAX_RESPONSE_SIZE) -> bytes:
    """
    HTTP yanıtını bellek taşmasına (DoS) karşı korumalı şekilde akış halinde okur.
    Maksimum boyutu aşan yanıtlar ResponseTooLargeError fırlatır.
    """
    # 1. Content-Length başlığı kontrolü
    content_length = response.headers.get("content-length")
    if content_length and content_length.isdigit():
        if int(content_length) > max_size:
            raise ResponseTooLargeError(
                f"Sunucu yanıt boyutu ({int(content_length)} bayt) izin verilen sınırı ({max_size} bayt) aşıyor."
            )

    # 2. Akış halinde parça parça oku ve boyutu sınırla
    chunks = []
    total_bytes = 0
    async for chunk in response.aiter_bytes():
        total_bytes += len(chunk)
        if total_bytes > max_size:
            raise ResponseTooLargeError(
                f"İndirilen veri boyutu izin verilen sınırı ({max_size} bayt) aştı."
            )
        chunks.append(chunk)

    return b"".join(chunks)
