from click.testing import CliRunner
from resmi_gazete_cli import __version__
from resmi_gazete_cli.cli.main import cli


def test_cli_version():
    """CLI sürüm parametresinin doğru çalıştığını test eder."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_help():
    """CLI yardım metninin görüntülenebildiğini test eder."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "T.C. Resmi Gazete CLI aracı" in result.output
