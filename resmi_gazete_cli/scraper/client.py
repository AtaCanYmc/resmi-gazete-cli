import datetime
import logging
import ssl
from typing import Union, Dict, Optional
import httpx

from .models import DailyGazette
from .parser import parse_gazette_html

logger = logging.getLogger(__name__)


def normalize_iso_date(target_date: Union[str, datetime.date]) -> str:
    """Tarih girdisini 'YYYY-MM-DD' formatına dönüştürür."""
    if isinstance(target_date, (datetime.date, datetime.datetime)):
        return target_date.strftime("%Y-%m-%d")

    date_str = str(target_date).strip()
    if "." in date_str:
        return datetime.datetime.strptime(date_str, "%d.%m.%Y").strftime("%Y-%m-%d")
    elif "/" in date_str:
        return datetime.datetime.strptime(date_str, "%d/%m/%Y").strftime("%Y-%m-%d")

    return date_str


class ResmiGazeteClient:
    """T.C. Resmi Gazete (resmigazete.gov.tr) için HTTP istemcisi."""

    BASE_URL = "https://resmigazete.gov.tr"
    FILTER_ENDPOINT = f"{BASE_URL}/Home/Filter"

    def __init__(
        self,
        timeout: int = 30,
        verify: Union[bool, str, ssl.SSLContext] = True
    ):
        self.timeout = timeout
        self.verify = verify
        self.headers: Dict[str, str] = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
        }

    async def _fetch_and_parse(self, url: str) -> DailyGazette:
        """Belirtilen URL'ye istek atarak HTML yanıtını ayrıştırır ve hataları yönetir."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers,
                verify=self.verify,
                follow_redirects=True
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
                return parse_gazette_html(response.text, base_url=self.BASE_URL)

        except httpx.TimeoutException as e:
            logger.error(f"Zaman aşımı hatası: {e}")
            return DailyGazette(error=f"İstek zaman aşımına uğradı ({self.timeout}s): {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP Durum Hatası ({e.response.status_code}): {e}")
            if e.response.status_code == 404:
                return DailyGazette(error="Resmi Gazete içeriği bulunamadı (404 Not Found).")
            return DailyGazette(error=f"Sunucu hatası ({e.response.status_code}): {str(e)}")
        except httpx.RequestError as e:
            logger.error(f"Bağlantı hatası: {e}")
            return DailyGazette(error=f"Bağlantı hatası oluştu: {str(e)}")
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return DailyGazette(error=f"Beklenmeyen bir hata oluştu: {str(e)}")

    async def get_todays_gazette(self) -> DailyGazette:
        """Günün yayımlanan Resmi Gazete içeriğini çeker ve modeller."""
        return await self._fetch_and_parse(self.BASE_URL)

    async def get_gazette_by_date(
        self,
        tarih: Union[str, datetime.date],
        mukerrer: Optional[int] = None
    ) -> DailyGazette:
        """Belirtilen tarih ve mükerrer numarasına göre Resmi Gazete içeriğini çeker."""
        try:
            iso_date = normalize_iso_date(tarih)
        except Exception as e:
            return DailyGazette(error=f"Geçersiz tarih formatı: {e}. 'GG.AA.YYYY' veya 'YYYY-MM-DD' kullanın.")

        url = f"{self.BASE_URL}/fihrist?tarih={iso_date}"
        if mukerrer is not None:
            url += f"&mukerrer={mukerrer}"

        gazette = await self._fetch_and_parse(url)

        # Eğer sayfada içerik veya tarih eşleşmiyorsa
        if not gazette.error and not gazette.items and not gazette.tarih:
            return DailyGazette(
                error=f"Belirtilen tarihte ({iso_date}) yayımlanmış Resmi Gazete sayısı bulunamadı."
            )

        return gazette
