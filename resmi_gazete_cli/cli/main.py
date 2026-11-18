import asyncio
import json
import unicodedata
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markup import escape

from resmi_gazete_cli import __version__
from resmi_gazete_cli.scraper import ResmiGazeteClient, SearchCriteria, SearchResponse

console = Console()

MEVZUAT_ALIASES = {
    "anayasa": "0010.02",
    "kanun": "0010",
    "kanunlar": "0010",
    "kararname": "0010.03",
    "cb-kararname": "0010.03",
    "cb-karar": "0010.04",
    "cumhurbaskani-karari": "0010.04",
    "yonetmelik": "0450.01",
    "yonetmelikler": "0450.01",
    "teblig": "0500",
    "tebligler": "0500",
    "genelge": "0490",
    "genelgeler": "0490",
    "aym": "0540",
    "anayasa-mahkemesi": "0540",
    "yargitay": "0550",
    "danistay": "0560",
    "sayistay": "0610",
    "atama": "0280",
}

MUKERRER_ALIASES = {
    "hayir": "HAYIR",
    "false": "HAYIR",
    "0": "HAYIR",
    "evet": "EVET",
    "true": "EVET",
    "1": "EVET",
    "2": "EVET2",
    "3": "EVET3",
    "4": "EVET4",
    "5": "EVET5",
}


def tr_lower(text: str) -> str:
    """Türkçe İ/ı ve I/ı karakterlerini koruyarak küçük harfe çevirir."""
    if not text:
        return ""
    tr_map = str.maketrans({"İ": "i", "I": "ı"})
    return unicodedata.normalize("NFC", text.translate(tr_map).lower())


def render_search_markdown(response: SearchResponse) -> str:
    """Arama sonuçlarını Markdown tablosu olarak formatlar."""
    md_lines = [
        f"# Resmi Gazete Arama Sonuçları (Toplam: {response.total_count}, Sayfa: {response.page})\n",
        "| # | Tarih | Sayı | Mevzuat Türü | No | Başlık / Konu | Bağlantı |",
        "| :---: | :---: | :---: | :--- | :---: | :--- | :--- |"
    ]
    start_idx = (response.page - 1) * response.page_size
    for idx, item in enumerate(response.results, start=start_idx + 1):
        tarih_str = item.tarih or "-"
        sayi_str = str(item.resmi_gazete_sayisi or "-")
        tur_str = item.mevzuat_adi or "-"
        no_str = item.kanun_karar_no or "-"
        konu_str = item.konu.replace("|", "/")
        link_str = f"[Görüntüle]({item.url})" if item.url else "-"
        md_lines.append(f"| {idx} | {tarih_str} | {sayi_str} | {tur_str} | {no_str} | {konu_str} | {link_str} |")
    return "\n".join(md_lines)


def render_search_table(response: SearchResponse, filter_desc: str) -> None:
    """Arama sonuçlarını Rich terminal tablosu olarak ekrana basar."""
    safe_filter = escape(filter_desc)
    panel = Panel(
        f"[bold white]Resmi Gazete Arama Sonuçları[/bold white]\n"
        f"[dim]Filtreler: {safe_filter}[/dim]\n"
        f"[green]Toplam Bulunan Kayıt: {response.total_count}[/green] [dim](Sayfa {response.page})[/dim]",
        border_style="cyan",
        expand=False
    )
    console.print(panel)

    if not response.results:
        console.print("[yellow]Arama kriterlerine uygun sonuç bulunamadı.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan", expand=True)
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Tarih", style="yellow", width=12)
    table.add_column("Sayı", style="cyan", width=8)
    table.add_column("Tür", style="magenta", width=20)
    table.add_column("No", style="green", width=10)
    table.add_column("Başlık / Konu", style="white")
    table.add_column("Bağlantı", style="blue")

    start_idx = (response.page - 1) * response.page_size
    for idx, item in enumerate(response.results, start=start_idx + 1):
        table.add_row(
            str(idx),
            escape(item.tarih or "-"),
            escape(str(item.resmi_gazete_sayisi or "-")),
            escape(item.mevzuat_adi or "-"),
            escape(item.kanun_karar_no or "-"),
            escape(item.konu),
            escape(item.url or "-")
        )

    console.print(table)


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(__version__, "-v", "--version", message="%(prog)s %(version)s")
def cli(ctx):
    """T.C. Resmi Gazete CLI aracı."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(daily)


@cli.command()
@click.option(
    "-d", "--date",
    default=None,
    help="Görüntülenecek gazete tarihi (GG.AA.YYYY veya YYYY-MM-DD formatında). Varsayılan: Güncel sayı."
)
@click.option(
    "-m", "--mukerrer",
    default=None,
    type=int,
    help="Mükerrer sayısı (Örnek: 1 veya 2)."
)
@click.option(
    "-c", "--category",
    default=None,
    help="Belirli bir bölüme veya kategoriye göre filtrele (Örnek: Cumhurbaşkanı, Yönetmelik, Tebliğ, İlan)."
)
@click.option(
    "-j", "--json-output",
    is_flag=True,
    default=False,
    help="Sonuçları JSON formatında yazdırır."
)
def daily(date, mukerrer, category, json_output):
    """Günün veya belirtilen tarihteki Resmi Gazete içeriklerini listeler."""
    async def run_fetch():
        client = ResmiGazeteClient()
        if date:
            return await client.get_gazette_by_date(date, mukerrer=mukerrer)
        return await client.get_todays_gazette()

    gazette = asyncio.run(run_fetch())

    if gazette.error:
        if json_output:
            console.print(json.dumps({"error": gazette.error}, ensure_ascii=False, indent=2))
        else:
            console.print(f"[bold red]Hata:[/bold red] {escape(gazette.error)}")
        return

    items = gazette.items
    if category:
        cat_query = tr_lower(category)
        items = [
            it for it in items
            if (it.kategori and cat_query in tr_lower(it.kategori)) or
               (it.bolum and cat_query in tr_lower(it.bolum)) or
               (it.alt_kategori and cat_query in tr_lower(it.alt_kategori)) or
               (cat_query in tr_lower(it.baslik))
        ]

    if json_output:
        output_data = {
            "tarih": gazette.tarih,
            "sayi": gazette.sayi,
            "mukerrer": gazette.mukerrer,
            "mukerrer_no": gazette.mukerrer_no,
            "total_count": len(items),
            "items": [it.model_dump() for it in items]
        }
        console.print(json.dumps(output_data, ensure_ascii=False, indent=2))
        return

    header_title = f"{gazette.tarih or 'Tarih Belirtilmemiş'} Tarihli ve {gazette.sayi or '-'} Sayılı Resmî Gazete"
    if gazette.mukerrer:
        header_title += f" ({gazette.mukerrer_no or 'Mükerrer'})"

    safe_header = escape(header_title)
    panel = Panel(
        f"[bold white]{safe_header}[/bold white]\n"
        f"[dim]Listelenen Karar ve İlan Sayısı: {len(items)}[/dim]",
        border_style="blue",
        expand=False
    )
    console.print(panel)

    if not items:
        console.print("[yellow]Filtreye uygun karar veya ilan bulunamadı.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold cyan", expand=True)
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Bölüm / Kategori", style="magenta", width=32)
    table.add_column("Başlık", style="white")
    table.add_column("Bağlantı", style="blue")

    for idx, item in enumerate(items, 1):
        cat_display = item.kategori or item.bolum or "-"
        link_display = item.link or "-"
        table.add_row(
            str(idx),
            escape(cat_display),
            escape(item.baslik),
            escape(link_display)
        )

    console.print(table)


@cli.command()
@click.option("-k", "--kelime", default="", help="Aranacak anahtar kelime veya kelime öbeği.")
@click.option("-b", "--baslangic", default="", help="Başlangıç Tarihi (GG.AA.YYYY veya YYYY-MM-DD).")
@click.option("-e", "--bitis", default="", help="Bitiş Tarihi (GG.AA.YYYY veya YYYY-MM-DD).")
@click.option("-s", "--sayi", default="", help="Resmi Gazete sayısı.")
@click.option("-n", "--mevzuat-no", default="", help="Kanun veya Karar numarası.")
@click.option("-t", "--mevzuat-turu", default="", help="Mevzuat türü kodu veya takma adı (kanun, teblig, yonetmelik vb.).")
@click.option("-m", "--mukerrer", default="", help="Mükerrer filtresi ('hayir', 'evet', '1', '2' vb.).")
@click.option("-p", "--page", default=1, type=int, help="Sayfa numarası (varsayılan: 1).")
@click.option("-l", "--page-size", default=10, type=int, help="Sayfa başına sonuç sayısı (varsayılan: 10).")
@click.option(
    "-f", "--format", "output_format",
    type=click.Choice(["table", "json", "md"], case_sensitive=False),
    default="table",
    help="Çıktı formatı: 'table' (varsayılan), 'json' veya 'md' (Markdown)."
)
def search(kelime, baslangic, bitis, sayi, mevzuat_no, mevzuat_turu, mukerrer, page, page_size, output_format):
    """Resmi Gazete arama sisteminde (/Home/Filter) detaylı filtreleme yapar."""
    tur_normalized = tr_lower(mevzuat_turu.strip())
    resolved_tur = MEVZUAT_ALIASES.get(tur_normalized, mevzuat_turu.strip())
    mukerrer_normalized = tr_lower(mukerrer.strip())
    resolved_mukerrer = MUKERRER_ALIASES.get(mukerrer_normalized, mukerrer.strip())

    criteria = SearchCriteria(
        kelime=kelime,
        baslangic_tarihi=baslangic,
        bitis_tarihi=bitis,
        sayi=sayi,
        mevzuat_sayisi=mevzuat_no,
        mevzuat_turu=resolved_tur,
        mukerrer=resolved_mukerrer,
        page=page,
        page_size=page_size
    )

    async def run_search():
        client = ResmiGazeteClient()
        return await client.search(criteria)

    response = asyncio.run(run_search())

    if response.error:
        if output_format.lower() == "json":
            console.print(json.dumps({"error": response.error}, ensure_ascii=False, indent=2))
        else:
            console.print(f"[bold red]Arama Hatası:[/bold red] {escape(response.error)}")
        return

    if output_format.lower() == "json":
        console.print(json.dumps(response.model_dump(), ensure_ascii=False, indent=2))
        return

    if output_format.lower() == "md":
        console.print(render_search_markdown(response))
        return

    filter_details = []
    if kelime:
        filter_details.append(f"Kelime: '{kelime}'")
    if baslangic or bitis:
        filter_details.append(f"Tarih: {baslangic or '...'} - {bitis or '...'}")
    if sayi:
        filter_details.append(f"Sayı: {sayi}")
    if resolved_tur:
        filter_details.append(f"Tür Kodu: {resolved_tur}")

    filter_desc = " | ".join(filter_details) if filter_details else "Tüm Kayıtlar"
    render_search_table(response, filter_desc)


if __name__ == "__main__":
    cli()
