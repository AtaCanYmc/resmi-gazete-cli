# Yol Haritası (Roadmap)

Bu belge, `resmi-gazete-cli` projesinin sürüm hedeflerini ve planlanan teknik kilometre taşlarını listeler.

---

## v0.1.0: Temel İskelet ve Asenkron İstemci (Mevcut)

- [x] Hatchling tabanlı `pyproject.toml` paketleme altyapısının kurulması.
- [x] Modüler mimarinin oluşturulması (`scraper`, `cli`, `mcp`).
- [x] `GazetteItem` ve `DailyGazette` Pydantic veri modellerinin tanımlanması.
- [x] `httpx.AsyncClient` tabanlı `ResmiGazeteClient` iskeletinin ve hata yönetiminin yazılması.
- [x] Repository governance dosyalarının (`LICENSE`, `SECURITY`, `CONTRIBUTING`) eklenmesi.

---

## v0.2.0: Günlük Gazete Scraping ve CLI Arayüzü (Tamamlandı)

- [x] `resmigazete.gov.tr` ana sayfasından günün sayısı, tarihi ve bölüm başlıklarının HTML parsing mantığının yazılması (`BeautifulSoup4` / `lxml`).
- [x] Yürütme ve İdare, Yargı ve İlanlar bölümlerinin kategorize edilerek yapısal modellere dönüştürülmesi.
- [x] `resmi-gazete-cli daily` komutunun eklenmesi ve `rich` kütüphanesi ile renklendirilmiş tablo çıktısı.
- [x] Mükerrer sayıların tespiti ve listelenmesi.
- [x] Çevrimdışı ve mock yanıtlar için birim testlerinin `tests/test_parser.py`, `tests/test_client.py` ve `tests/test_cli.py` altında yazılması.

---

## v0.3.0: Arama Endpoint'i ve Filtreleme (Tamamlandı)

- [x] `resmigazete.gov.tr/Home/Filter` endpoint'ine uygun arama isteği parametrelerinin `SearchCriteria` modeline bağlanması.
- [x] Kelime, tarih aralığı, sayı, mevzuat numarası ve mevzuat türüne göre arama desteği (takma adlarla).
- [x] `resmi-gazete-cli search` komutunun terminale kazandırılması.
- [x] Arama sonuçlarının Tablo, JSON veya Markdown formatında dışa aktarımı (`--format table/json/md`).

---

## v0.4.0: Model Context Protocol (FastMCP) Entegrasyonu

- [ ] `FastMCP` stdio sunucusunun tamamlanması (`resmi-gazete-mcp`).
- [ ] `get_todays_gazette` MCP aracının LLM ajanlarına açılması.
- [ ] `search_gazette` MCP aracının parametrik filtrelerle entegre edilmesi.
- [ ] Claude Desktop ve Cursor yapılandırma rehberinin dokümantasyona eklenmesi.
