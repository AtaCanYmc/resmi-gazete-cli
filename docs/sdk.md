# Python SDK ve API Referansı

[← Dokümantasyon İndeksine Dön](index.md) | [← Ana Dokümantasyon (README.md)](../README.md)

`resmi-gazete-cli`, harici Python projelerine kütüphane (`SDK`) olarak doğrudan dahil edilebilir. Tam tip desteği, asenkron G/Ç mimarisi ve Pydantic V2 veri doğrulaması sunar.

---

## İçindekiler

- [Kurulum](#kurulum)
- [ResmiGazeteClient](#resmigazeteclient)
  - [İstemci Başlatma](#istemci-başlatma)
  - [get_todays_gazette](#get_todays_gazette)
  - [get_gazette_by_date](#get_gazette_by_date)
  - [search](#search)
  - [get_document_text](#get_document_text)
- [Pydantic Veri Modelleri](#pydantic-veri-modelleri)
- [Hata Yönetimi (Exceptions)](#hata-yönetimi)
- [Kod Tarifleri ve Örnekler](#kod-tarifleri)

---

## Kurulum

```bash
pip install resmi-gazete-cli
```

---

## ResmiGazeteClient

Modül yolu: `resmi_gazete_cli.scraper.client.ResmiGazeteClient`

`httpx.AsyncClient` üzerine inşa edilmiş, bağlantı havuzunu (connection pool) yöneten ve Resmî Gazete uç noktalarıyla konuşan ana istemci sınıfıdır.

### İstemci Başlatma

İstemci, asenkron bağlam yöneticisi (`async with`) kalıbıyla kullanılmalıdır:

```python
import asyncio
from resmi_gazete_cli import ResmiGazeteClient

async def main():
    async with ResmiGazeteClient(timeout=30.0) as client:
        # İstemci çağrıları
        pass

asyncio.run(main())
```

Kurucu Parametreleri:
- `timeout` (`float`, varsayılan `30.0`): HTTP istekleri için saniye cinsinden zaman aşımı sınırı.
- `base_url` (`str`, varsayılan `"https://resmigazete.gov.tr"`): Uç nokta kök URL adresi.

### get_todays_gazette

Günün Resmî Gazete sayısını indirir ve hiyerarşik nesneye dönüştürür.

```python
gazette = await client.get_todays_gazette()
print(f"Tarih: {gazette.date}, Sayı: {gazette.number}")
```

- **Dönüş Değeri**: `GazetteDay` nesnesi.
- **Olası Hatalar**: `NetworkError`, `NotFoundError`, `ParseError`.

### get_gazette_by_date

Belirtilen tarihe ait gazeteyi çeker.

```python
gazette = await client.get_gazette_by_date(date="15.11.2024", mukerrer=False)
```

- **Parametreler**:
  - `date` (`str` veya `datetime.date`): `GG.AA.YYYY` veya `YYYY-MM-DD` formatında tarih.
  - `mukerrer` (`bool`, varsayılan `False`): Mükerrer sayı kontrolü.
- **Dönüş Değeri**: `GazetteDay` nesnesi.

### search

`resmigazete.gov.tr/Home/Filter` DataTables API'sine asenkron POST isteği gönderir.

```python
from resmi_gazete_cli.scraper.models import SearchCriteria

criteria = SearchCriteria(
    kelime="yapay zeka",
    mevzuat_turu="4",  # Yönetmelikler
    page=1,
    page_size=10,
)
response = await client.search(criteria)

print(f"Toplam Kayıt: {response.records_total}")
for item in response.data:
    print(f"- [{item.resmi_gazete_tarihi}] {item.baslik} ({item.link})")
```

- **Parametreler**:
  - `criteria` (`SearchCriteria`): Arama kriterlerini barındıran Pydantic modeli.
- **Dönüş Değeri**: `SearchResponse` nesnesi.

### get_document_text

Verilen mevzuat linkindeki HTM içeriğini çeker, `windows-1254` kodlamasını çözer ve temiz metin olarak döndürür.

```python
text = await client.get_document_text("https://resmigazete.gov.tr/eskiler/2024/11/20241115-1.htm")
```

---

## Pydantic Veri Modelleri

Modül yolu: `resmi_gazete_cli.scraper.models`

| Model Sınıfı | Alanlar | Açıklama |
| --- | --- | --- |
| `GazetteItem` | `title: str`, `url: str`, `item_type: Optional[str]`, `law_no: Optional[str]` | Tekil bir kanun, karar veya ilan maddesi. |
| `GazetteCategory` | `main_category: str`, `sub_category: Optional[str]`, `items: List[GazetteItem]` | Gazete bölümü (Yürütme ve İdare, Yargı vb.). |
| `GazetteDay` | `date: str`, `number: str`, `url: str`, `is_mukerrer: bool`, `categories: List[GazetteCategory]` | Tek bir güne ait gazete sayısı ve tüm bölümleri. |
| `SearchCriteria` | `kelime`, `baslangic_tarihi`, `bitis_tarihi`, `sayi`, `mevzuat_sayisi`, `mevzuat_turu`, `mukerrer`, `page`, `page_size` | Arama filtresi girdisi. |
| `SearchResultItem` | `kanun_karar_no`, `resmi_gazete_tarihi`, `resmi_gazete_sayisi`, `baslik`, `link` | Tekil arama sonucu kaydı. |
| `SearchResponse` | `draw: int`, `records_total: int`, `records_filtered: int`, `data: List[SearchResultItem]` | Sayfalanmış arama sonucu paketi. |

---

## Hata Yönetimi

Modül yolu: `resmi_gazete_cli.scraper.client`

Tüm özel istisnalar `ScraperError` taban sınıfından türetilmiştir:

```text
ScraperError
├── NetworkError     Ağ bağlantı hataları, DNS çözme sorunları, zaman aşımları
├── NotFoundError    Hedef gazete veya belgenin bulunamaması (HTTP 404)
└── ParseError       HTML yapısının beklenenden farklı olması veya DOM bozulması
```

Örnek Hata Yakalama Kalıbı:

```python
from resmi_gazete_cli import ResmiGazeteClient
from resmi_gazete_cli.scraper.client import NotFoundError, NetworkError, ScraperError

async with ResmiGazeteClient() as client:
    try:
        gazette = await client.get_gazette_by_date("01.01.1920")
    except NotFoundError:
        print("Belirtilen tarihte yayımlanmış gazete sayısı bulunamadı.")
    except NetworkError as e:
        print(f"Bağlantı kurulamadı: {e}")
    except ScraperError as e:
        print(f"Genel kazıma hatası: {e}")
```

---

## Kod Tarifleri

### Tüm İlan Başlıklarını Düz Liste Haline Getirme

```python
import asyncio
from resmi_gazete_cli import ResmiGazeteClient

async def extract_all_titles():
    async with ResmiGazeteClient() as client:
        today = await client.get_todays_gazette()
        all_titles = [
            item.title
            for cat in today.categories
            for item in cat.items
        ]
        return all_titles

titles = asyncio.run(extract_all_titles())
print(f"Bugün toplam {len(titles)} adet mevzuat/karar yayımlandı.")
```
