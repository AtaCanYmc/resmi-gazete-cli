from typing import Optional, List
from pydantic import BaseModel, Field


class GazetteItem(BaseModel):
    """Resmi Gazete'de yayımlanan tekil bir karar, kanun veya ilan maddesi."""

    tarih: Optional[str] = Field(None, description="Resmi Gazete yayım tarihi (örn. 18.11.2026)")
    sayi: Optional[str] = Field(None, description="Resmi Gazete sayısı (örn. 32726)")
    kategori: Optional[str] = Field(None, description="Bölüm veya Kategori (örn. Yürütme ve İdare, Tebliğler, İlanlar)")
    baslik: str = Field(..., description="Karar, ilan veya mevzuat başlığı")
    link: Optional[str] = Field(None, description="Karara veya ilana ait tam bağlantı linki")


class DailyGazette(BaseModel):
    """Günün Resmi Gazete sayısı ve içerik listesi."""

    tarih: Optional[str] = Field(None, description="Gazete tarihi")
    sayi: Optional[str] = Field(None, description="Gazete sayısı")
    mukerrer: bool = Field(False, description="Mükerrer sayı olup olmadığı")
    items: List[GazetteItem] = Field(default_factory=list, description="Yayımlanan maddeler")
    error: Optional[str] = Field(None, description="Oluşan hata mesajı (varsa)")
