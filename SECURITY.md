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
