import subprocess
import re
import requests
from bs4 import BeautifulSoup

# Функция для запуска скана nmap
def run_nmap_scan(target):
    subprocess.run(['nmap', "-A", "--script", "vulners", "--script-args", "mincvss=3", target], check=True)

# Функция для запуска скана gobuster
def run_gobuster_scan(target, wordlist):
    subprocess.run(['gobuster', 'dir', '-u', target, '-w', wordlist, '-t', '50'], check=True)

# Функция для запуска скана gobuster для субдоменов
def run_gobuster_subdomains_scan(target, wordlist):
    result = subprocess.run(['gobuster', 'fuzz', '-u', f'FUZZ.{target}', '-w', wordlist], capture_output=True, text=True)
    found_subdomains = [line.split()[-1] for line in result.stdout.splitlines() if "Found:" in line]
    return found_subdomains

# Функция для извлечения адресов электронной почты и телефонов из веб-страницы
def extract_contacts(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', str(soup))
    phones = re.findall(r'\+\d[\d\s()+-]+', str(soup))
    return emails, phones

# Запрос целевого адреса
# Новый запрос пути к словарю
wordlist = input("Введите путь к словарю для gobuster: ")
target = input("Введите целевой адрес (домен или IP): ")

# Проверка типа адреса и выполнение соответствующих действий
if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target):
    # Если адрес IP, запускаем скан nmap
    run_nmap_scan(target)
else:
    # Удаление http:// или https://, если они есть
    target = target.replace("http://", "").replace("https://", "")

    # Если домен, извлекаем контакты и почтовые адреса
    emails, phones = extract_contacts(f"http://{target}")
    print(f"Найденные телефоны: {phones}")
    print(f"Найденные адреса электронной почты: {emails}")

    # Из адресов почт выделяем домены и проверяем, отличаются ли они от вводного
    domains = set(email.split('@')[1] for email in emails)
    for domain in domains:
        if domain != target:
            print(f"Запускаем скан nmap для домена: {domain}")
            run_nmap_scan(domain)

    # Запускаем программу gobuster для первоначального и найденных доменов
    print("Запускаем скан gobuster для первоначального и найденных доменов")
    for domain in domains.union({target}):
        run_gobuster_scan(domain, wordlist)
        subdomains = run_gobuster_subdomains_scan(domain, wordlist)
        if subdomains:
            print(f"Найденные субдомены для {domain}: {subdomains}")

# Сохраняем результаты сканов для всех доменов и субдоменов
all_results = []
if re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target):
    # IP: только nmap
    nmap_result = subprocess.run(['nmap', "-A", "--script", "vulners", "--script-args", "mincvss=3", target], capture_output=True, text=True)
    all_results.append({
        'target': target,
        'type': 'ip',
        'nmap': nmap_result.stdout
    })
else:
    # ... существующий код ...
    all_domains = list(domains.union({target}))
    all_subdomains = {}
    for domain in all_domains:
        nmap_result = subprocess.run(['nmap', "-A", "--script", "vulners", "--script-args", "mincvss=3", domain], capture_output=True, text=True)
        gobuster_result = subprocess.run(['gobuster', 'dir', '-u', domain, '-w', wordlist, '-t', '50'], capture_output=True, text=True)
        subdomains = run_gobuster_subdomains_scan(domain, wordlist)
        all_subdomains[domain] = subdomains
        all_results.append({
            'target': domain,
            'type': 'domain',
            'nmap': nmap_result.stdout,
            'gobuster': gobuster_result.stdout,
            'subdomains': subdomains
        })
    # Повторный запуск сканирования для найденных субдоменов (1 уровень)
    for domain in all_domains:
        subdomains = all_subdomains.get(domain, [])
        for sub in subdomains:
            nmap_result = subprocess.run(['nmap', "-A", "--script", "vulners", "--script-args", "mincvss=3", sub], capture_output=True, text=True)
            gobuster_result = subprocess.run(['gobuster', 'dir', '-u', sub, '-w', wordlist, '-t', '50'], capture_output=True, text=True)
            sub_subdomains = run_gobuster_subdomains_scan(sub, wordlist)
            all_results.append({
                'target': sub,
                'type': 'subdomain',
                'nmap': nmap_result.stdout,
                'gobuster': gobuster_result.stdout,
                'subdomains': sub_subdomains
            })
# Сохраняем всё в файл
with open('scan_results.txt', 'w') as f:
    f.write("==============================\n")
    f.write(f"SurfaceHarvester Scan Report\n")
    f.write("==============================\n\n")
    f.write(f"Исходная цель: {target}\n\n")
    if not re.match(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target):
        f.write(f"[Контакты]\nТелефоны: {phones}\nПочта: {emails}\n\n")
    for res in all_results:
        f.write("------------------------------\n")
        f.write(f"Цель: {res['target']}\nТип: {res['type']}\n")
        if 'nmap' in res:
            f.write("[Nmap]\n")
            f.write(res['nmap'] + "\n")
        if 'gobuster' in res:
            f.write("[Gobuster]\n")
            f.write(res['gobuster'] + "\n")
        if 'subdomains' in res and res['subdomains']:
            f.write("[Субдомены]\n")
            for sub in res['subdomains']:
                f.write(sub + "\n")
        f.write("\n")
    f.write("Конец отчёта\n")