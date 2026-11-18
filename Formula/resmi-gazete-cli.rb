class ResmiGazeteCli < Formula
  include Language::Python::Virtualenv

  desc "T.C. Resmi Gazete Karar, Kanun ve İlan Scraper, CLI ve MCP Sunucusu"
  homepage "https://github.com/AtaCanYmc/resmi-gazete-cli"
  url "https://github.com/AtaCanYmc/resmi-gazete-cli/archive/refs/tags/v0.1.2.tar.gz"
  sha256 "3e49fec54ab8837ed213c87853f41c6fd66ba95fae01389daffc25526dcd7ccd"
  license "Apache-2.0"
  head "https://github.com/AtaCanYmc/resmi-gazete-cli.git", branch: "main"

  depends_on "python@3.12"

  def install
    virtualenv_create(libexec, "python3.12")
    system libexec/"bin/pip", "install", "--upgrade", "pip", "setuptools"
    system libexec/"bin/pip", "install", buildpath
    bin.install_symlink libexec/"bin/resmi-gazete-cli"
    bin.install_symlink libexec/"bin/resmi-gazete-mcp"
  end

  test do
    assert_match "resmi-gazete-cli", shell_output("#{bin}/resmi-gazete-cli --version")
  end
end
