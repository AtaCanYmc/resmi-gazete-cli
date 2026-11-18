import re
from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from .models import GazetteItem, DailyGazette


def clean_item_title(raw_title: str) -> str:
    """Başlığın başındaki tire ve harf/sayı numaralandırmalarını temizler."""
    cleaned = re.sub(r"^(?:[–—\-]+|[a-z0-9]\s*[-–—])\s*", "", raw_title).strip()
    return cleaned if cleaned else raw_title.strip()


def parse_gazette_html(html_content: str, base_url: str = "https://resmigazete.gov.tr") -> DailyGazette:
    """Resmi Gazete HTML içeriğini parse ederek DailyGazette modeline dönüştürür."""
    soup = BeautifulSoup(html_content, "html.parser")

    # 1. Tarih, Sayı ve Mükerrer tespiti
    tarih_val: Optional[str] = None
    sayi_val: Optional[str] = None
    mukerrer_val = False
    mukerrer_no_val: Optional[str] = None

    header_elem = soup.find("div", class_="tarih") or soup.find("div", class_="preview-title")
    header_text = header_elem.get_text(" ", strip=True) if header_elem else ""

    # Eğer header elemanı bulunamadıysa tüm sayfadaki başlık formatını ara
    if not header_text:
        match_candidate = soup.find(string=re.compile(r"\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{4}[^\n\r]{0,120}?Sayılı"))
        if match_candidate:
            header_text = str(match_candidate).strip()

    date_issue_match = re.search(
        r"(\d{1,2}\s+[A-Za-zÇĞİÖŞÜçğıöşü]+\s+\d{4})\s+Tarihli\s+ve\s+(\d+)\s+Sayılı",
        header_text
    )
    if date_issue_match:
        tarih_val = date_issue_match.group(1).strip()
        sayi_val = date_issue_match.group(2).strip()

    mukerrer_match = re.search(r"(\d+\.\s*Mükerrer|Mükerrer)", header_text, re.IGNORECASE)
    if mukerrer_match:
        mukerrer_val = True
        mukerrer_no_val = mukerrer_match.group(1).strip()

    # 2. Bölüm ve İlanların (Fihrist) Ayrıştırılması
    items = []
    current_main: Optional[str] = None
    current_sub: Optional[str] = None

    content_div = soup.find("div", class_="html-content")
    elements = content_div.find_all("div", recursive=False) if content_div else soup.find_all("div")

    for el in elements:
        classes = el.get("class", [])
        if "html-title" in classes:
            current_main = el.get_text(strip=True)
            current_sub = None
        elif "html-subtitle" in classes:
            current_sub = el.get_text(strip=True)
        elif "fihrist-item" in classes:
            a_tag = el.find("a")
            raw_text = a_tag.get_text(strip=True) if a_tag else el.get_text(strip=True)
            if not raw_text:
                continue

            cleaned_title = clean_item_title(raw_text)
            href = a_tag.get("href") if a_tag else None
            link = urljoin(base_url, href) if href else None

            kategori_parts = [p for p in [current_main, current_sub] if p]
            full_category = " / ".join(kategori_parts) if kategori_parts else None

            item = GazetteItem(
                tarih=tarih_val,
                sayi=sayi_val,
                bolum=current_main,
                alt_kategori=current_sub,
                kategori=full_category,
                baslik=cleaned_title,
                link=link
            )
            items.append(item)

    return DailyGazette(
        tarih=tarih_val,
        sayi=sayi_val,
        mukerrer=mukerrer_val,
        mukerrer_no=mukerrer_no_val,
        items=items
    )
