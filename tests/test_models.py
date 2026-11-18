import pytest
from pydantic import ValidationError
from resmi_gazete_cli.scraper.models import (
    GazetteItem,
    DailyGazette,
    SearchCriteria,
    SearchResultItem,
    SearchResponse
)


def test_gazette_item_valid():
    """GazetteItem modelinin geçerli alanlarla doğru oluştuğunu doğrular."""
    item = GazetteItem(
        tarih="18.11.2026",
        sayi="32726",
        kategori="Yürütme ve İdare",
        baslik="Cumhurbaşkanı Kararı (Karar Sayısı: 2026/1)",
        link="https://resmigazete.gov.tr/eskiler/2026/11/20261118-1.pdf"
    )

    assert item.tarih == "18.11.2026"
    assert item.sayi == "32726"
    assert item.kategori == "Yürütme ve İdare"
    assert item.baslik == "Cumhurbaşkanı Kararı (Karar Sayısı: 2026/1)"
    assert item.link == "https://resmigazete.gov.tr/eskiler/2026/11/20261118-1.pdf"


def test_gazette_item_missing_required_baslik():
    """Zorunlu olan 'baslik' alanı verilmediğinde ValidationError fırlatılmalıdır."""
    with pytest.raises(ValidationError):
        GazetteItem(
            tarih="18.11.2026",
            sayi="32726"
        )


def test_daily_gazette_defaults():
    """DailyGazette varsayılan değerlerinin (boş liste, mukerrer=False) doğrulanması."""
    gazette = DailyGazette()

    assert gazette.tarih is None
    assert gazette.sayi is None
    assert gazette.mukerrer is False
    assert gazette.items == []
    assert gazette.error is None


def test_daily_gazette_with_items_and_error():
    """DailyGazette nesnesinin elemanlar ve hata ile birlikte oluşturulması."""
    item = GazetteItem(baslik="Tebliğ")
    gazette = DailyGazette(
        tarih="18.11.2026",
        sayi="32726",
        mukerrer=True,
        items=[item],
        error="Kısmi içerik"
    )

    assert gazette.mukerrer is True
    assert len(gazette.items) == 1
    assert gazette.items[0].baslik == "Tebliğ"
    assert gazette.error == "Kısmi içerik"


def test_search_criteria_defaults_and_validation():
    """SearchCriteria modelinin varsayılan değerleri ve sınır doğrulaması."""
    criteria = SearchCriteria()
    assert criteria.page == 1
    assert criteria.page_size == 10
    assert criteria.kelime == ""

    # Sayfa numarası 0 veya negatif olamaz
    with pytest.raises(ValidationError):
        SearchCriteria(page=0)

    # Sayfa boyutu 100'den büyük olamaz
    with pytest.raises(ValidationError):
        SearchCriteria(page_size=101)


def test_search_result_and_response_models():
    """SearchResultItem ve SearchResponse modellerinin doğrulanması."""
    item = SearchResultItem(
        konu="Vergi Usul Kanunu Genel Tebliği",
        mevzuat_adi="TEBLİĞLER",
        resmi_gazete_sayisi=33426,
        kanun_karar_no="597",
        tarih="10.11.2026",
        mukerrer="HAYIR",
        url="https://resmigazete.gov.tr/fihrist?tarih=2026-11-10"
    )
    response = SearchResponse(
        total_count=1,
        page=1,
        page_size=10,
        results=[item]
    )

    assert response.total_count == 1
    assert len(response.results) == 1
    assert response.results[0].konu == "Vergi Usul Kanunu Genel Tebliği"
    assert response.error is None
