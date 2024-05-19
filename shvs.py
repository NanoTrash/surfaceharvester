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
        run_gobuster_scan(domain, '/Users/kostenko.evgeny/Desktop/1212/big.txt')
        subdomains = run_gobuster_subdomains_scan(domain, '/Users/kostenko.evgeny/Desktop/1212/big.txt')
        if subdomains:
            print(f"Найденные субдомены для {domain}: {subdomains}")

# Сохранение результатов в txt файл
with open('scan_results.txt', 'w') as f:
    f.write(f"Результаты сканов для адреса: {target}\n")
    f.write(f"Найденные телефоны: {phones}\n")
    f.write(f"Найденные адреса электронной почты: {emails}\n")
    f.write("Результаты сканов nmap:\n")
    nmap_result = subprocess.run(['nmap', "-A", "--script", "vulners", "--script-args", "mincvss=3", target], capture_output=True, text=True)
    f.write(nmap_result.stdout)
    f.write("Результаты сканов gobuster:\n")
    gobuster_result = subprocess.run(['gobuster', 'dir', '-u', target, '-w', '/Users/kostenko.evgeny/Desktop/1212/big.txt', '-t', '50'], capture_output=True, text=True)
    f.write(gobuster_result.stdout)
    f.write("Результаты сканов gobuster для субдоменов:\n")
    gobuster_subdomains_result = subprocess.run(['gobuster', 'fuzz', '-u', f'FUZZ.{target}', '-w', '/Users/kostenko.evgeny/Desktop/1212/big.txt'], capture_output=True, text=True)
    f.write(gobuster_subdomains_result.stdout)