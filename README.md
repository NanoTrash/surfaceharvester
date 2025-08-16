# SurfaceHarvester

Автоматизированный сбор информации о поверхности (сканирование портов, директорий, субдоменов, контактов).

## Особенности
- Асинхронное извлечение контактов с сайтов (aiohttp)
- Валидация входных данных и логирование ошибок
- Использование context7.json для автоматизации рекомендаций и исключения лишних файлов
- Сканирование портов (nmap), директорий (gobuster dir), фаззинг параметров (gobuster fuzz) и субдоменов (subfinder)

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

# Установите subfinder (https://github.com/projectdiscovery/subfinder)
curl -sSfL https://install.goreleaser.com/github.com/projectdiscovery/subfinder.sh | sh
# Или используйте инструкции с официального репозитория
```

## Быстрый старт
1. Установите зависимости через Poetry:
   ```bash
   poetry install
   ```
2. Убедитесь, что nmap, gobuster и subfinder установлены в системе
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

## Использование subfinder

Subfinder используется для поиска субдоменов каждой уникальной цели (доменов). Результаты поиска субдоменов выводятся в отчёте в соответствующем разделе для каждого домена.

- Subfinder должен быть установлен и доступен в PATH.
- Для каждой цели subfinder запускается только один раз.

## Использование двух словарей (wordlists)

Скрипт использует два разных словаря:

1. **Для gobuster dir** — поиск директорий и потенциальных точек с параметрами (например, /download?file=):
   - Пример: `/usr/share/seclists/Discovery/Web-Content/common.txt`
   - Путь к словарю пользователь указывает при запуске (input)
2. **Для gobuster fuzz** — фаззинг найденных параметров (например, LFI):
   - Пример: `/usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt`
   - Путь к словарю пользователь указывает при запуске (input)

**Порядок работы:**
- Сначала скрипт спрашивает путь к словарю для gobuster dir
- Затем спрашивает путь к словарю для gobuster fuzz
- После этого выполняется поиск директорий, анализируются найденные параметры, и для них запускается fuzzing с выбранным словарём

Все выбранные словари отражаются в отчёте.
