import datetime
import logging
import ssl
from typing import Union, Dict, Optional, Any, List
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import httpx

from .models import DailyGazette, SearchCriteria, SearchResponse, SearchResultItem, GazetteDocument
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


def safe_iso_date(target_date: Optional[Union[str, datetime.date]]) -> str:
    """Tarih girdisini doğrular ve boş değilse 'YYYY-MM-DD' formatına çevirir."""
    if not target_date:
        return ""
    return normalize_iso_date(target_date)


def to_tr_date_format(target_date: Optional[Union[str, datetime.date]]) -> str:
    """Tarih girdisini 'GG.AA.YYYY' formatına dönüştürür."""
    if not target_date:
        return ""
    if isinstance(target_date, (datetime.date, datetime.datetime)):
        return target_date.strftime("%d.%m.%Y")

    date_str = str(target_date).strip()
    if "-" in date_str:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
    elif "/" in date_str:
        return datetime.datetime.strptime(date_str, "%d/%m/%Y").strftime("%d.%m.%Y")

    return date_str


def build_filter_payload(criteria: SearchCriteria) -> Dict[str, Any]:
    """DataTables POST isteği için JSON gövdesini oluşturur."""
    start_offset = (criteria.page - 1) * criteria.page_size
    baslangic_iso = safe_iso_date(criteria.baslangic_tarihi)
    bitis_iso = safe_iso_date(criteria.bitis_tarihi)

    return {
        "draw": criteria.page,
        "start": start_offset,
        "length": criteria.page_size,
        "columns": [],
        "order": [],
        "search": {"value": "", "regex": False},
        "parameters": {
            "searchtype": "1",
            "genelaranacakkelime": criteria.kelime or "",
            "genelbaslangictarihi": baslangic_iso,
            "genelbitistarihi": bitis_iso,
            "genelsayi": str(criteria.sayi or ""),
            "genelmevzuatsayisi": str(criteria.mevzuat_sayisi or ""),
            "genelmukerrer": str(criteria.mukerrer or ""),
            "genelmevzuatturu": str(criteria.mevzuat_turu or ""),
            "genelkurumkodu": str(criteria.kurum_kodu or ""),
        }
    }


def parse_search_items(raw_items: List[Dict[str, Any]], base_url: str) -> List[SearchResultItem]:
    """Sunucudan dönen ham JSON listesini SearchResultItem modellerine dönüştürür."""
    results = []
    for item in raw_items:
        item_url = item.get("url")
        full_url = urljoin(base_url, item_url) if item_url else None
        tarih_display = item.get("resmiGazeteTarihiFormatted") or item.get("resmiGazeteTarihi")

        results.append(SearchResultItem(
            konu=item.get("konu") or "",
            mevzuat_adi=item.get("mevzuatAdi"),
            resmi_gazete_sayisi=item.get("resmiGazeteSayisi"),
            kanun_karar_no=item.get("kanunKararNo"),
            tarih=tarih_display,
            mukerrer=item.get("mukerrer"),
            mukerrer_sayisi=item.get("mukerrerSayisi"),
            url=full_url
        ))
    return results


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

        if not gazette.error and not gazette.items and not gazette.tarih:
            return DailyGazette(
                error=f"Belirtilen tarihte ({iso_date}) yayımlanmış Resmi Gazete sayısı bulunamadı."
            )

        return gazette

    async def search(self, criteria: SearchCriteria) -> SearchResponse:
        """Resmi Gazete arama sisteminde (/Home/Filter) filtreleme sorgusu yürütür."""
        try:
            payload = build_filter_payload(criteria)
        except Exception as e:
            return SearchResponse(error=f"Arama parametresi hatası: {e}")

        search_headers = dict(self.headers)
        search_headers.update({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/",
        })

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=search_headers,
                verify=self.verify,
                follow_redirects=True
            ) as client:
                response = await client.post(self.FILTER_ENDPOINT, json=payload)
                response.raise_for_status()

                data = response.json()
                total_count = data.get("recordsFiltered", data.get("recordsTotal", 0))
                results = parse_search_items(data.get("data", []), base_url=self.BASE_URL)

                return SearchResponse(
                    total_count=total_count,
                    page=criteria.page,
                    page_size=criteria.page_size,
                    results=results
                )

        except httpx.TimeoutException as e:
            logger.error(f"Arama zaman aşımı: {e}")
            return SearchResponse(error=f"Arama isteği zaman aşımına uğradı ({self.timeout}s): {str(e)}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Arama HTTP hatası ({e.response.status_code}): {e}")
            return SearchResponse(error=f"Arama sunucu hatası ({e.response.status_code}): {str(e)}")
        except httpx.RequestError as e:
            logger.error(f"Arama bağlantı hatası: {e}")
            return SearchResponse(error=f"Arama bağlantı hatası: {str(e)}")
        except Exception as e:
            logger.error(f"Arama beklenmeyen hata: {e}")
            return SearchResponse(error=f"Arama sırasında beklenmeyen bir hata oluştu: {str(e)}")

    async def get_document_content(self, url: str) -> GazetteDocument:
        """Verilen Resmi Gazete doküman URL'sinden (HTM/HTML) metin içeriğini çeker."""
        target_url = url if url.startswith("http") else urljoin(self.BASE_URL, url)

        if target_url.lower().endswith(".pdf"):
            return GazetteDocument(
                url=target_url,
                content_type="application/pdf",
                icerik=(
                    f"Bu doküman doğrudan bir PDF dosyasıdır: {target_url}\n"
                    "PDF içeriğini incelemek için PDF okuyucu veya markitdown aracını kullanabilirsiniz."
                )
            )

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout,
                headers=self.headers,
                verify=self.verify,
                follow_redirects=True
            ) as client:
                response = await client.get(target_url)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, "html.parser", from_encoding="windows-1254")
                for tag in soup(["script", "style"]):
                    tag.decompose()

                text = soup.get_text(separator="\n", strip=True)
                return GazetteDocument(
                    url=str(response.url),
                    content_type="text/html",
                    icerik=text
                )

        except httpx.TimeoutException as e:
            logger.error(f"Doküman zaman aşımı: {e}")
            return GazetteDocument(
                url=target_url,
                error=f"Doküman indirme zaman aşımına uğradı ({self.timeout}s): {str(e)}"
            )
        except httpx.HTTPStatusError as e:
            logger.error(f"Doküman HTTP hatası ({e.response.status_code}): {e}")
            return GazetteDocument(
                url=target_url,
                error=f"Doküman bulunamadı ({e.response.status_code}): {str(e)}"
            )
        except Exception as e:
            logger.error(f"Doküman okuma hatası: {e}")
            return GazetteDocument(
                url=target_url,
                error=f"Doküman okunurken bir hata oluştu: {str(e)}"
            )
