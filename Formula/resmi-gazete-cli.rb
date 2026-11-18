class ResmiGazeteCli < Formula
  include Language::Python::Virtualenv

  desc "T.C. Resmi Gazete Karar, Kanun ve İlan Scraper, CLI ve MCP Sunucusu"
  homepage "https://github.com/AtaCanYmc/resmi-gazete-cli"
  url "https://github.com/AtaCanYmc/resmi-gazete-cli/archive/refs/tags/v0.1.3.tar.gz" # x-release-please-version
  sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  license "Apache-2.0"
  head "https://github.com/AtaCanYmc/resmi-gazete-cli.git", branch: "main"

  depends_on "cryptography"
  depends_on "python@3.12"

  uses_from_macos "libxml2"
  uses_from_macos "libxslt"

  resource "annotated-doc" do
    url "https://files.pythonhosted.org/packages/0f/6e/a61e86e43bb6039b31a33a8f5fba76fe1cdacf3661e7b9756d4ff1b28cdc/annotated_doc-0.0.6.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "annotated-types" do
    url "https://files.pythonhosted.org/packages/5f/56/a8120250d128bed162cd73c76d45f6ef9991f3e068f62a8ee060afa3104a/annotated_types-0.8.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "anyio" do
    url "https://files.pythonhosted.org/packages/a1/98/7e457a3b014976887a050561955c0b76e1e7e2d6e27b78ecef2ef80518f2/anyio-4.16.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "attrs" do
    url "https://files.pythonhosted.org/packages/9a/8e/82a0fe20a541c03148528be8cac2408564a6c9a0cc7e9171802bc1d26985/attrs-26.1.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "beautifulsoup4" do
    url "https://files.pythonhosted.org/packages/43/65/318323f98dbee45d42dff61d8f047181bc6f2268a9068cfad035a46be5af/beautifulsoup4-4.15.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "certifi" do
    url "https://files.pythonhosted.org/packages/fd/11/b524cbd9bbdaca58608e4cf4053fd463417549e1959fa8d3aa18319f9555/certifi-2026.10.23.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "cffi" do
    url "https://files.pythonhosted.org/packages/9e/ef/008a1939e372c06329a3fce4279c02f328488f3526744906eeec3da7ad5f/cffi-2.1.1.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "click" do
    url "https://files.pythonhosted.org/packages/45/37/edbf1b0707709013c0cf2e8317e03d97ed29bf4cac709fe328904ae92a38/click-8.5.1.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "h11" do
    url "https://files.pythonhosted.org/packages/01/ee/02a2c011bdab74c6fb3c75474d40b3052059d95df7e73351460c8588d963/h11-0.16.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "httpcore" do
    url "https://files.pythonhosted.org/packages/06/94/82699a10bca87a5556c9c59b5963f2d039dbd239f25bc2a63907a05a14cb/httpcore-1.0.9.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "httpcore2" do
    url "https://files.pythonhosted.org/packages/92/9d/df40b41f7db0370f82019820709244e7b660c52aa3da3c9e5c4e8141f6e6/httpcore2-2.16.2.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "httpx" do
    url "https://files.pythonhosted.org/packages/b1/df/48c586a5fe32a0f01324ee087459e112ebb7224f646c0b5023f5e79e9956/httpx-0.28.1.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "httpx2" do
    url "https://files.pythonhosted.org/packages/1c/77/6515121dc5ac3c743ad1bff5afe635bcd1a3f23cc40db3c5c89f7d02917d/httpx2-2.16.2.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "idna" do
    url "https://files.pythonhosted.org/packages/f5/08/8eea9d4b8302028f3abb2c0813953f7aec26d33b7a8960ed760e65ff29fa/idna-3.20.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "jsonschema" do
    url "https://files.pythonhosted.org/packages/b3/fc/e067678238fa451312d4c62bf6e6cf5ec56375422aee02f9cb5f909b3047/jsonschema-4.26.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "jsonschema-specifications" do
    url "https://files.pythonhosted.org/packages/19/74/a633ee74eb36c44aa6d1095e7cc5569bebf04342ee146178e2d36600708b/jsonschema_specifications-2025.9.1.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "lxml" do
    url "https://files.pythonhosted.org/packages/23/ad/28ecd7cb894d172f3c9c80a075eeeb2017ac62e3632cee05a5f9493547eb/lxml-6.1.3.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/16/fc/cee2c45553c9a9bf77d8b0c391560c556d7ed756b1f0bb35eb5d48db09ea/markdown_it_py-4.3.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "mcp" do
    url "https://files.pythonhosted.org/packages/9d/8d/e0d339616f4810e9051d4aba6887afab289ab1f81875fe908b606cdfd0e3/mcp-2.3.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "mcp-types" do
    url "https://files.pythonhosted.org/packages/9e/2d/7c251e34207f6c51000312fc8839111ac45cfe02023f90b44e7f1051dd8e/mcp_types-2.3.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/d6/54/cfe61301667036ec958cb99bd3efefba235e65cdeb9c84d24a8293ba1d90/mdurl-0.1.2.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "opentelemetry-api" do
    url "https://files.pythonhosted.org/packages/19/14/cf3a6b6448849656e1e5f4e2101f3988dc6789724050096aba1bc5ccf592/opentelemetry_api-1.45.2.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "pycparser" do
    url "https://files.pythonhosted.org/packages/cb/27/eeb9f307bf07060f3d9f9aa0fb8c15b01bdfded0a941e4b2719c7f94cacd/pycparser-3.12.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "pydantic" do
    url "https://files.pythonhosted.org/packages/b4/fc/1203d011145c98ddce3cd2f505bb54375ef8d43223053df6bfcf3c746f46/pydantic-2.14.3.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "pydantic-core" do
    url "https://files.pythonhosted.org/packages/9c/0f/34f9ce4ba701dd0b815033ef94d99b56f66200e578ee6052aa3ac26f064e/pydantic_core-2.50.4.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "pygments" do
    url "https://files.pythonhosted.org/packages/49/2e/ced460408999b33da6b31b0021b0f37d329e202d4169aeb164493778f25b/pygments-2.21.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "pyjwt" do
    url "https://files.pythonhosted.org/packages/43/ea/5194e52748b0da83d71e082d75496eaec6e58f419f5e184786ded517e6a9/pyjwt-2.15.1.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "python-dotenv" do
    url "https://files.pythonhosted.org/packages/74/26/2fbeedb218a787a5eea551c7532cac4e009f83d689dd2faa0d0353473f86/python_dotenv-1.2.4.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "python-multipart" do
    url "https://files.pythonhosted.org/packages/7e/c0/c753d487a83d873f6946cee6cbc26cea3fe59a476ad0de99a14938a2fbd8/python_multipart-0.0.34.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "referencing" do
    url "https://files.pythonhosted.org/packages/22/f5/df4e9027acead3ecc63e50fe1e36aca1523e1719559c499951bb4b53188f/referencing-0.37.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/c0/8f/0722ca900cc807c13a6a0c696dacf35430f72e0ec571c4275d2371fca3e9/rich-15.0.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "rpds-py" do
    url "https://files.pythonhosted.org/packages/42/68/3bd46b8a5e01d3c2ebdf9c5e9497912e3fe0cde02bac21a7130ca866e403/rpds_py-2026.9.1.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "shellingham" do
    url "https://files.pythonhosted.org/packages/58/15/8b3609fd3830ef7b27b655beb4b4e9c62313a4e8da8c676e142cc210d58e/shellingham-1.5.4.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "soupsieve" do
    url "https://files.pythonhosted.org/packages/1f/52/ee5646b65d98a252e807ccc37725363942372a4113072e0bce7ed22f8b84/soupsieve-4.1.1.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "sse-starlette" do
    url "https://files.pythonhosted.org/packages/41/43/a232e3cd804293bd4f6d01e8895bc0f6f83ea148d712baf9d783c7d93d23/sse_starlette-3.7.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "starlette" do
    url "https://files.pythonhosted.org/packages/48/bb/3d8757f21e9a53d9035c9eb039a777047139a16bfdbedfc7a58241c3d914/starlette-1.10.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "truststore" do
    url "https://files.pythonhosted.org/packages/ee/9f/c5201d42a484c061e528825fc8e2d565f5abd50a4ced6fb7d29c4ec99b2b/truststore-0.10.5.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/6c/aa/0de7986aa1fa856adb961c67345189b97d13f6e250b34ba68884df865f07/typer-0.29.1.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "typing-extensions" do
    url "https://files.pythonhosted.org/packages/f6/cc/6253133b5bb138fc3306cebfbda2c520f545d36b5be2c7255cc528bb45d6/typing_extensions-4.16.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "typing-inspection" do
    url "https://files.pythonhosted.org/packages/ff/50/0195198eb1d75bab716bb0a813abea4cc394bfa17a92a189f021a34859af/typing_inspection-0.4.5.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  resource "uvicorn" do
    url "https://files.pythonhosted.org/packages/da/34/30e9280707135d2cfc589dfff3cb796bd07a3aeb1a3e415ba09dd89d7bb4/uvicorn-0.54.0.tar.gz"
    sha256 "6a5d7f45e613c735e2ad516d86c40d84659eed506b68c080546cd09d4c0b858a"
  end

  def install
    venv = virtualenv_create(libexec, "python3.12", system_site_packages: true)
    venv.pip_install resources
    venv.pip_install_and_link buildpath
  end

  test do
    assert_match "resmi-gazete-cli", shell_output("#{bin}/resmi-gazete-cli --help")
    assert_match "resmi-gazete-mcp", shell_output("#{bin}/resmi-gazete-mcp --help")
  end
end
