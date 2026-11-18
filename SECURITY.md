# Güvenlik Politikası (Security Policy)

Bu belge, `resmi-gazete-cli` projesinde güvenlik zafiyetlerinin nasıl bildirileceğini ve ele alınacağını açıklar.

---

## Desteklenen Sürümler

Aşağıdaki tabloda güvenlik güncellemelerini aktif olarak alan sürümler listelenmiştir:

| Sürüm | Destek Durumu |
| --- | --- |
| `0.1.x` | Destekleniyor |
| `< 0.1.0` | Desteklenmiyor |

---

## Yerleşik Güvenlik Mekanizmaları

`resmi-gazete-cli`, LLM ve terminal ortamlarında güvenli çalıştırma için aşağıdaki savunma mekanizmalarını uygular:

1. **SSRF ve İzin Verilmeyen URL Koruması (`is_safe_url`):**
   - HTTP/HTTPS istekleri yalnızca doğrulanmış kamu alan adları (`resmigazete.gov.tr`, `mevzuat.gov.tr` ve alt alan adları) ile sınırlandırılmıştır.
   - Yerel ağ (LAN), döngüsel (`127.0.0.1`, `::1`), özel IP blokları (`10.0.0.0/8`, `192.168.0.0/16`, `172.16.0.0/12`) ve bulut metadata adresleri (`169.254.169.254`) kesin olarak engellenir.
   - HTTP yönlendirme (`redirect`) zincirindeki tüm ara hedefler açık yönlendirme (`Open Redirect`) tabanlı SSRF atlatmalarına karşı doğrulanır.

2. **DoS ve Bellek Taşması Koruması (`MAX_RESPONSE_SIZE`):**
   - İndirilen yanıtlar ve doküman gövdeleri 10 MB tavan boyutuyla sınırlandırılmıştır. Sınırı aşan yanıtlar bellek tüketilmeden önce derhal kesilir.

3. **Terminal Markup ve Enjeksiyon Koruması (`rich.markup.escape`):**
   - Resmî Gazete başlıkları, mevzuat metinleri ve kullanıcı arama girdileri Rich konsolunda görüntülenmeden önce kaçış (`escape`) işleminden geçirilir. Bu sayede sahte terminal bağlantıları (`phishing links`) ve biçimlendirme çökmeleri önlenir.

4. **Düzenli İfade Güvenliği (ReDoS Önleme):**
   - Tarih ve sayı ayrıştırma desenlerindeki sınırsız açgözlü niceleyiciler (`.*`) sınırlandırılmıştır.

---

## Güvenlik Zafiyeti Bildirimi

Bir güvenlik açığı veya zafiyet tespit ettiğinizde lütfen bunu **herkese açık issue listesinde paylaşmayın**.

Bildirimlerinizi aşağıdaki kanallardan biri üzerinden gizli olarak iletin:

1. **GitHub Security Advisory (Önerilen):** Proje deposundaki "Security" sekmesi altından özel güvenlik bildirimi (Report a vulnerability) açın.
2. **E-posta:** Zafiyet detaylarını doğrudan `atacanymc@gmail.com` adresine gönderin.

### Bildirimde Bulunması Gereken Bilgiler

- Zafiyetin türü ve etkilenen bileşen (ör. `ResmiGazeteClient`, `CLI`, `FastMCP`).
- Zafiyeti yerel ortamda tetikleyen adımlar ve örnek girdi verileri.
- Tespit edilen etki (ör. TLS atlatma, veri bozulması, yetkisiz dosya erişimi).

---

## Yanıt Süresi ve Süreç

- **İlk Yanıt:** Bildirimler en geç **48 saat** içinde incelenir ve alındı onayı verilir.
- **Değerlendirme ve Yama:** Zafiyet doğrulandıktan sonra en kısa sürede düzeltme hazırlanır, test edilir ve yeni bir sürüm etiketi ile yayınlanır.
- **Koordineli Açıklama:** Düzeltme yayınlandıktan sonra zafiyet detayları koordineli bir şekilde kamuoyu ile paylaşılır.
