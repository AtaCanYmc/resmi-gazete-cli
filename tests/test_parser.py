from resmi_gazete_cli.scraper.parser import parse_gazette_html, clean_item_title


def test_clean_item_title():
    """Başlık temizleme fonksiyonunun farklı tire ve önekleri temizlediğini doğrular."""
    assert clean_item_title("–– Cumhurbaşkanı Kararı (No: 1)") == "Cumhurbaşkanı Kararı (No: 1)"
    assert clean_item_title("– Yönetmelik Başlığı") == "Yönetmelik Başlığı"
    assert clean_item_title("a - Yargı İlânları") == "Yargı İlânları"
    assert clean_item_title("b - Artırma ve Eksiltme") == "Artırma ve Eksiltme"
    assert clean_item_title("Normal Başlık") == "Normal Başlık"


def test_parse_gazette_html_standard():
    """Standart günlük Resmi Gazete HTML içeriğinin ayrıştırılması."""
    sample_html = """
    <div class="row tarih mt-3 mt-sm-0">18 Kasım 2026 Tarihli ve 33434 Sayılı Resmî Gazete</div>
    <div class="html-content">
        <div class="card-title html-title">YÜRÜTME VE İDARE BÖLÜMÜ</div>
        <div class="html-subtitle">CUMHURBAŞKANI KARARLARI</div>
        <div class="fihrist-item mb-1">
            <a href="/eskiler/2026/11/20261118-1.pdf">–– Örnek Karar 1</a>
        </div>
        <div class="html-subtitle">YÖNETMELİK</div>
        <div class="fihrist-item mb-1">
            <a href="/eskiler/2026/11/20261118-2.htm">–– Örnek Yönetmelik</a>
        </div>
        <div class="card-title html-title">İLÂN BÖLÜMÜ</div>
        <div class="fihrist-item mb-1">
            <a href="/ilanlar/20261118-1.htm">a - Yargı İlânları</a>
        </div>
    </div>
    """

    gazette = parse_gazette_html(sample_html, base_url="https://resmigazete.gov.tr")

    assert gazette.tarih == "18 Kasım 2026"
    assert gazette.sayi == "33434"
    assert gazette.mukerrer is False
    assert len(gazette.items) == 3

    # İlk eleman
    item1 = gazette.items[0]
    assert item1.baslik == "Örnek Karar 1"
    assert item1.bolum == "YÜRÜTME VE İDARE BÖLÜMÜ"
    assert item1.alt_kategori == "CUMHURBAŞKANI KARARLARI"
    assert item1.kategori == "YÜRÜTME VE İDARE BÖLÜMÜ / CUMHURBAŞKANI KARARLARI"
    assert item1.link == "https://resmigazete.gov.tr/eskiler/2026/11/20261118-1.pdf"

    # İkinci eleman
    item2 = gazette.items[1]
    assert item2.baslik == "Örnek Yönetmelik"
    assert item2.alt_kategori == "YÖNETMELİK"

    # İlan bölümü elemanı
    item3 = gazette.items[2]
    assert item3.baslik == "Yargı İlânları"
    assert item3.bolum == "İLÂN BÖLÜMÜ"
    assert item3.alt_kategori is None
    assert item3.kategori == "İLÂN BÖLÜMÜ"


def test_parse_gazette_html_mukerrer():
    """Mükerrer Resmi Gazete HTML içeriğinin ayrıştırılması."""
    sample_html = """
    <div class="preview-title">27 Ekim 2026 Tarihli ve 33413 Sayılı Resmî Gazete 1. Mükerrer</div>
    <div class="html-content">
        <div class="card-title html-title">YÜRÜTME VE İDARE BÖLÜMÜ</div>
        <div class="html-subtitle">CUMHURBAŞKANI KARARI</div>
        <div class="fihrist-item mb-1">
            <a href="https://www.resmigazete.gov.tr/eskiler/2026/10/20261027M1-1.pdf">
                –– 2027 Yılı Cumhurbaşkanlığı Yıllık Programının Onaylanması
            </a>
        </div>
    </div>
    """

    gazette = parse_gazette_html(sample_html)

    assert gazette.tarih == "27 Ekim 2026"
    assert gazette.sayi == "33413"
    assert gazette.mukerrer is True
    assert gazette.mukerrer_no == "1. Mükerrer"
    assert len(gazette.items) == 1
    assert "Cumhurbaşkanlığı Yıllık Programı" in gazette.items[0].baslik
