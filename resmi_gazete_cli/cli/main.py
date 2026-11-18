import asyncio
import json
import unicodedata
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from resmi_gazete_cli import __version__
from resmi_gazete_cli.scraper import ResmiGazeteClient

console = Console()


def tr_lower(text: str) -> str:
    """Türkçe İ/ı ve I/ı karakterlerini koruyarak küçük harfe çevirir."""
    if not text:
        return ""
    tr_map = str.maketrans({"İ": "i", "I": "ı"})
    return unicodedata.normalize("NFC", text.translate(tr_map).lower())


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
            console.print(f"[bold red]Hata:[/bold red] {gazette.error}")
        return

    # Kategori filtreleme
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

    # JSON Çıktısı
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

    # Terminal Rich Tablosu
    header_title = f"{gazette.tarih or 'Tarih Belirtilmemiş'} Tarihli ve {gazette.sayi or '-'} Sayılı Resmî Gazete"
    if gazette.mukerrer:
        header_title += f" ({gazette.mukerrer_no or 'Mükerrer'})"

    panel = Panel(
        f"[bold white]{header_title}[/bold white]\n"
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
            cat_display,
            item.baslik,
            link_display
        )

    console.print(table)


if __name__ == "__main__":
    cli()
