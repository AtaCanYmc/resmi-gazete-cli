from resmi_gazete_cli.scraper.models import GazetteItem, DailyGazette


def test_gazette_models():
    """Temel Pydantic veri modellerinin doğruluğunu test eder."""
    item = GazetteItem(
        tarih="18.11.2026",
        sayi="32726",
        kategori="Yürütme ve İdare",
        baslik="Örnek Karar Başlığı",
        link="https://resmigazete.gov.tr/eskiler/2026/11/20261118-1.pdf"
    )

    gazette = DailyGazette(
        tarih="18.11.2026",
        sayi="32726",
        items=[item]
    )

    assert gazette.tarih == "18.11.2026"
    assert gazette.sayi == "32726"
    assert len(gazette.items) == 1
    assert gazette.items[0].baslik == "Örnek Karar Başlığı"
    assert gazette.error is None
