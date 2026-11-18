# CLI Kullanım Kılavuzu

[← Dokümantasyon İndeksine Dön](index.md) | [← Ana Dokümantasyon (README.md)](../README.md)

`resmi-gazete-cli`, terminal ortamında Resmî Gazete sayılarını listelemek, filtrelemek ve arama yapmak üzere tasarlanmış modern bir komut satırı aracıdır.

---

## İçindekiler

- [Komut Hiyerarşisi](#komut-hiyerarşisi)
- [resmi-gazete-cli daily](#resmi-gazete-cli-daily)
  - [Parametreler ve Seçenekler](#daily-parametreler)
  - [Kullanım Örnekleri](#daily-örnekler)
- [resmi-gazete-cli search](#resmi-gazete-cli-search)
  - [Parametreler ve Seçenekler](#search-parametreler)
  - [Mevzuat Türü Kısayolları](#mevzuat-türü-kısayolları)
  - [Formatlama Seçenekleri](#formatlama-seçenekleri)
  - [Kullanım Örnekleri](#search-örnekler)
- [Çıkış Kodları (Exit Codes)](#çıkış-kodları)

---

## Komut Hiyerarşisi

```text
resmi-gazete-cli [GLOBAL SEÇENEKLER] KOMUT [ARGÜMANLAR]
├── daily    Belirli bir günün Resmî Gazete içeriğini listeler
└── search   Resmî Gazete arşivinde anahtar kelime ve mevzuat türüyle arama yapar
```

Global Seçenekler:
- `--help`: Yardım iletisini ve kullanılabilir komutları yazdırır.

---

## resmi-gazete-cli daily

`daily` komutu, belirtilen tarihe ait Resmî Gazete içeriğini çeker; ana bölümler (Yürütme ve İdare, Yargı, İlân) ve alt kategoriler bazında yapılandırılmış olarak listeler.

### Daily Parametreler

| Seçenek | Kısa | Tip | Varsayılan | Açıklama |
| --- | --- | --- | --- | --- |
| `--date` | `-d` | Metin (`GG.AA.YYYY`) | Bugün | Listelenecek gazete tarihi. |
| `--mukerrer` | `-m` | Bayrak (Boolean) | `False` | Mükerrer sayıyı sorgular. |
| `--category` | `-c` | Metin | Yok | Belirli bir kategori adına göre yerel filtreleme yapar. |
| `--json-output` | `-j` | Bayrak (Boolean) | `False` | Çıktıyı insan okunabilir tablo yerine ham JSON formatında üretir. |
| `--help` | | Bayrak | | Komut yardım iletisini gösterir. |

### Daily Örnekler

Bugünün gazetesini renkli terminal panelleriyle görüntüleme:
```bash
resmi-gazete-cli daily
```

Tarihsel bir sayıyı çekme:
```bash
resmi-gazete-cli daily -d 15.11.2024
```

Mükerrer sayıyı görüntüleme:
```bash
resmi-gazete-cli daily -d 15.11.2024 -m
```

Yalnızca belirli bir kategoriye (örneğin Yargı veya Tebliğ) ait maddeleri listeleme:
```bash
resmi-gazete-cli daily -c "YARGI"
```

Çıktıyı JSON olarak alıp `jq` aracına aktarma:
```bash
resmi-gazete-cli daily --json-output | jq '.categories[].items[] | .title'
```

---

## resmi-gazete-cli search

`search` komutu, `resmigazete.gov.tr/Home/Filter` uç noktası üzerinden DataTables arama sorguları yürütür. Arama sonuçları sayfalama, tarih filtresi ve mevzuat türü filtreleriyle daraltılabilir.

### Search Parametreler

| Seçenek | Kısa | Tip | Varsayılan | Açıklama |
| --- | --- | --- | --- | --- |
| `--kelime` | `-k` | Metin | `""` | Aranacak kelime veya tam ifade öbeği. |
| `--baslangic` | `-b` | Metin (`GG.AA.YYYY` veya `YYYY-MM-DD`) | Yok | Arama aralığı başlangıç tarihi. |
| `--bitis` | `-e` | Metin (`GG.AA.YYYY` veya `YYYY-MM-DD`) | Yok | Arama aralığı bitiş tarihi. |
| `--sayi` | `-s` | Metin | Yok | Resmî Gazete sayısı filtresi (ör. `32723`). |
| `--mevzuat-no` | `-n` | Metin | Yok | Kanun / Karar / Yönetmelik numarası (ör. `7524`). |
| `--mevzuat-turu`| `-t` | Metin | Yok | Mevzuat türü kodu veya kısayol adı. |
| `--mukerrer` | `-m` | Metin (`1`/`0`) | Yok | `1` mükerrer sayılar, `0` normal sayılar. |
| `--page` | `-p` | Tamsayı | `1` | Görüntülenecek sayfa numarası (1 tabanlı). |
| `--page-size` | `-l` | Tamsayı | `10` | Sayfa başına sonuç adedi (1 ile 100 arası). |
| `--format` | `-f` | Seçim (`table`, `json`, `md`) | `table` | Terminal çıktı biçimi. |

### Mevzuat Türü Kısayolları

`--mevzuat-turu` parametresine sayısal kod yerine aşağıdaki okunabilir kısayollar verilebilir:

| Kısayol | Sistem Kodu | Karşılık Gelen Mevzuat Türü |
| --- | --- | --- |
| `kanun` | `1` | Kanunlar |
| `cb-karar` | `3` | Cumhurbaşkanı Kararları |
| `yonetmelik` | `4` | Yönetmelikler |
| `teblig` | `5` | Tebliğler |
| `aym` | `7` | Anayasa Mahkemesi Kararları |
| `danistay` | `8` | Danıştay Kararları |
| `yargitay` | `9` | Yargıtay Kararları |

### Formatlama Seçenekleri

- **`table`**: Terminalde renkli, sütun hizalı Rich tablosu çizer. Etkileşimli terminal kullanımı için uygundur.
- **`json`**: Sonuçları tam meta verisiyle birlikte JSON dizisi olarak basar. Otomasyon betikleri ve boru hatları (`pipeline`) için uygundur.
- **`md`**: Markdown tablosu üretir. Dokümantasyon ve rapor dosyalarına doğrudan yönlendirilebilir.

### Search Örnekler

Anahtar kelime araması (varsayılan tablo çıktısı):
```bash
resmi-gazete-cli search -k "yapay zeka"
```

Tarih aralığı ve mevzuat türü filtresiyle arama:
```bash
resmi-gazete-cli search -k "enflasyon" -b 01.01.2024 -e 31.12.2024 -t teblig
```

Kanun numarası ile sorgu ve Markdown çıktısını dosyaya yazma:
```bash
resmi-gazete-cli search -n "7524" -f md > vergi_kanunu.md
```

Sonuçları 2. sayfadan 25 kayıt olacak şekilde JSON olarak alma:
```bash
resmi-gazete-cli search -k "enerji" -p 2 -l 25 -f json > enerji_sayfa2.json
```

---

## Çıkış Kodları

`resmi-gazete-cli`, kabuk otomasyonlarında güvenilir durum denetimi sağlamak için standart POSIX çıkış kodlarını kullanır:

| Çıkış Kodu | Durum | Anlamı |
| --- | --- | --- |
| `0` | Başarılı | İstek tamamlandı ve sonuçlar üretildi. |
| `1` | Hata | Ağ hatası, HTTP durum kodu (4xx/5xx), HTML ayrıştırma hatası veya geçersiz parametre girişi. |
