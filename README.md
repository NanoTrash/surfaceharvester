# SurfaceHarvester

Автоматизированный сбор информации о поверхности (сканирование портов, директорий, субдоменов, контактов).

## Особенности
- Асинхронное извлечение контактов с сайтов (aiohttp)
- Валидация входных данных и логирование ошибок
- Использование context7.json для автоматизации рекомендаций и исключения лишних файлов
- Сканирование портов (nmap), директорий и субдоменов (gobuster)

## Установка зависимостей (Ubuntu Linux)

```bash
# Установите Python и pip, если не установлены
sudo apt update
sudo apt install -y python3 python3-pip

# Установите Poetry (современный менеджер зависимостей Python)
pip install poetry

# Установите зависимости из pyproject.toml
poetry install

# Установите nmap
sudo apt install -y nmap

# Установите gobuster (Go должен быть установлен)
sudo apt install -y golang-go
GO111MODULE=on go install github.com/OJ/gobuster/v3@latest
# Добавьте gobuster в PATH (обычно ~/go/bin)
export PATH=$PATH:$(go env GOPATH)/bin
# Чтобы сделать это постоянным, добавьте строку выше в ~/.bashrc или ~/.zshrc
```

## Быстрый старт
1. Установите зависимости через Poetry:
   ```bash
   poetry install
   ```
2. Убедитесь, что nmap и gobuster установлены в системе
3. Запустите скрипт через Poetry:
   ```bash
   poetry run python shvs.py
   ```

## pyproject.toml
В корне проекта находится файл `pyproject.toml`, который описывает все Python-зависимости и метаданные проекта. Для установки используйте Poetry (см. выше).

## context7.json
В корне проекта находится файл `context7.json`, который содержит правила и исключения для автоматизации рекомендаций и индексации (MCP/Context7).

## Best practices
- Используйте только актуальные версии инструментов
- Не храните чувствительные данные в коде
- Все результаты сохраняются в scan_results.txt
- Обрабатывайте ошибки всех внешних вызовов
