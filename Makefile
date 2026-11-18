.PHONY: help install test lint build clean ci serve-docs

PYTHON ?= $(shell if [ -f .venv/bin/python ]; then echo .venv/bin/python; else echo python3; fi)
PIP ?= $(shell if [ -f .venv/bin/pip ]; then echo .venv/bin/pip; else echo pip; fi)

help: ## Mevcut komutları ve açıklamalarını listeler
	@echo "Kullanılabilir hedefler:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Geliştirme bağımlılıklarını ve paketi editable modda kurar
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	$(PIP) install flake8 pytest pytest-asyncio build

lint: ## Flake8 ile kod kalitesi ve sözdizimi denetimi yapar
	$(PYTHON) -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	$(PYTHON) -m flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

test: ## Tüm birim testlerini pytest ile çalıştırır
	$(PYTHON) -m pytest -v

build: ## Dağıtım paketlerini (sdist ve wheel) oluşturur ve twine ile doğrular
	$(PYTHON) -m build
	$(PYTHON) -m twine check --strict dist/*

clean: ## Geçici dosyaları, derleme çıktılarını ve önbellekleri temizler
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

ci: lint test build ## GitHub Actions CI adımlarının tamamını yerel ortamda koşturur

serve-docs: ## Dokümantasyon web arayüzünü yerel HTTP sunucusunda sunar (http://localhost:8000)
	@echo "Dokümantasyon arayüzü başlatılıyor: http://localhost:8000"
	$(PYTHON) -m http.server --directory site 8000

