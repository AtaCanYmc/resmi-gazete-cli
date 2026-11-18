import logging
import ssl
from typing import Union, Dict
import httpx

from .models import DailyGazette

logger = logging.getLogger(__name__)


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
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "X-Requested-With": "XMLHttpRequest",
        }

    async def get_todays_gazette(self) -> DailyGazette:
        """Günün yayımlanan Resmi Gazete içeriklerini çeker."""
        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers,
                verify=self.verify,
                follow_redirects=True
            ) as client:
                # İlerleyen aşamada günün gazetesini çekme ve parsing mantığı burada yer alacak.
                response = await client.get(self.BASE_URL)
                response.raise_for_status()

                # Şimdilik boş iskelet
                return DailyGazette(items=[])

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
