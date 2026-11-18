from typing import Optional, List, Union
from pydantic import BaseModel, Field


class GazetteItem(BaseModel):
    """Resmi Gazete'de yayımlanan tekil bir karar, kanun veya ilan maddesi."""

    tarih: Optional[str] = Field(None, description="Resmi Gazete yayım tarihi (örn. 18.11.2026)")
    sayi: Optional[str] = Field(None, description="Resmi Gazete sayısı (örn. 33434)")
    bolum: Optional[str] = Field(None, description="Ana Bölüm (örn. Yürütme ve İdare Bölümü, İlan Bölümü)")
    alt_kategori: Optional[str] = Field(None, description="Alt Kategori (örn. Cumhurbaşkanı Kararları, Yönetmelik)")
    kategori: Optional[str] = Field(None, description="Tam Kategori hiyerarşisi")
    baslik: str = Field(..., description="Karar, ilan veya mevzuat başlığı")
    link: Optional[str] = Field(None, description="Karara veya ilana ait tam bağlantı linki")


class DailyGazette(BaseModel):
    """Günün Resmi Gazete sayısı ve içerik listesi."""

    tarih: Optional[str] = Field(None, description="Gazete tarihi")
    sayi: Optional[str] = Field(None, description="Gazete sayısı")
    mukerrer: bool = Field(False, description="Mükerrer sayı olup olmadığı")
    mukerrer_no: Optional[str] = Field(None, description="Mükerrer sayısı (örn. 1. Mükerrer)")
    items: List[GazetteItem] = Field(default_factory=list, description="Yayımlanan maddeler")
    error: Optional[str] = Field(None, description="Oluşan hata mesajı (varsa)")


class SearchCriteria(BaseModel):
    """Resmi Gazete /Home/Filter arama kriterleri."""

    kelime: Optional[str] = Field("", description="Genel aranacak kelime veya kelime öbeği")
    baslangic_tarihi: Optional[str] = Field("", description="Başlangıç Tarihi (GG.AA.YYYY veya YYYY-MM-DD)")
    bitis_tarihi: Optional[str] = Field("", description="Bitiş Tarihi (GG.AA.YYYY veya YYYY-MM-DD)")
    sayi: Optional[str] = Field("", description="Resmi Gazete sayısı")
    mevzuat_sayisi: Optional[str] = Field("", description="Kanun/Karar/Mevzuat sayısı")
    mukerrer: Optional[str] = Field("", description="Mükerrer durumu ('', 'HAYIR', 'EVET', 'EVET2' vb.)")
    mevzuat_turu: Optional[str] = Field("", description="Mevzuat türü kodu (örn. '0010' KANUNLAR, '0500' TEBLİĞLER)")
    kurum_kodu: Optional[str] = Field("", description="Kurum kodu")
    page: int = Field(1, ge=1, description="Sayfa numarası (1-indexed)")
    page_size: int = Field(10, ge=1, le=100, description="Sayfa başı kayıt sayısı")


class SearchResultItem(BaseModel):
    """Resmi Gazete arama sonucu tekil maddesi."""

    konu: str = Field(..., description="Karar veya mevzuat konusu/başlığı")
    mevzuat_adi: Optional[str] = Field(None, description="Mevzuat kategorisi/adı (örn. KANUNLAR, TEBLİĞLER)")
    resmi_gazete_sayisi: Optional[Union[int, str]] = Field(None, description="Resmi Gazete sayısı")
    kanun_karar_no: Optional[str] = Field(None, description="Kanun veya Karar numarası")
    tarih: Optional[str] = Field(None, description="Resmi Gazete yayım tarihi (GG.AA.YYYY)")
    mukerrer: Optional[str] = Field(None, description="Mükerrer durumu (HAYIR, EVET vb.)")
    mukerrer_sayisi: Optional[Union[int, str]] = Field(None, description="Mükerrer sayısı (varsa)")
    url: Optional[str] = Field(None, description="Bağlantı URL'i")


class SearchResponse(BaseModel):
    """Resmi Gazete arama sorgusu yanıt modeli."""

    total_count: int = Field(0, description="Toplam eşleşen kayıt sayısı")
    page: int = Field(1, description="Mevcut sayfa numarası")
    page_size: int = Field(10, description="Sayfa başı kayıt sayısı")
    results: List[SearchResultItem] = Field(default_factory=list, description="Arama sonuçları")
    error: Optional[str] = Field(None, description="Hata mesajı (varsa)")
