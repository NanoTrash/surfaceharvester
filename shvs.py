import subprocess
import re
import aiohttp
import asyncio
import logging
from bs4 import BeautifulSoup
import os

logging.basicConfig(filename='surfaceharvester.log', level=logging.INFO, format='%(asctime)s %(levelname)s:%(message)s')

def validate_wordlist(wordlist_path):
    if not os.path.isfile(wordlist_path):
        logging.error(f"Wordlist file not found: {wordlist_path}")
        raise FileNotFoundError(f"Wordlist file not found: {wordlist_path}")

def validate_target(target):
    if not target:
        logging.error("Target is empty")
        raise ValueError("Target cannot be empty")

# Функция для запуска скана nmap
def run_nmap_scan(target):
    try:
        result = subprocess.run(['nmap', "-A", "--script", "vulners", "--script-args", "mincvss=3", target], capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        logging.error(f"[Nmap error for {target}]: {e}")
        return f"[Nmap error for {target}]: {e}\n"

# Функция для запуска скана gobuster (директории)
def run_gobuster_scan(target, wordlist):
    url = target if target.startswith('http') else f"http://{target}"
    try:
        result = subprocess.run(['gobuster', 'dir', '-u', url, '-w', wordlist, '-t', '50'], capture_output=True, text=True, check=True)
        return result.stdout
    except Exception as e:
        logging.error(f"[Gobuster error for {target}]: {e}")
        return f"[Gobuster error for {target}]: {e}\n"

# Функция для запуска скана gobuster для субдоменов (dns)
def run_gobuster_subdomains_scan(target, wordlist):
    try:
        result = subprocess.run(['gobuster', 'dns', '-d', target, '-w', wordlist, '--wildcard'], capture_output=True, text=True, check=True)
        found_subdomains = [line.split()[-1] for line in result.stdout.splitlines() if "Found:" in line]
        return found_subdomains
    except Exception as e:
        logging.error(f"[Gobuster subdomain error for {target}]: {e}")
        return [f"[Gobuster subdomain error for {target}]: {e}"]

# Асинхронная функция для извлечения адресов электронной почты и телефонов из веб-страницы
async def extract_contacts(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html.parser')
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', str(soup))
                phones = re.findall(r'\+\d[\d\s()+-]+', str(soup))
                return emails, phones
    except Exception as e:
        logging.error(f"[Extract contacts error for {url}]: {e}")
        return [], []

async def main():
    wordlist = input("Введите путь к словарю для gobuster: ")
    target = input("Введите целевой адрес (домен или IP): ")
    try:
        validate_wordlist(wordlist)
        validate_target(target)
    except Exception as e:
        print(f"Ошибка валидации: {e}")
        return

    emails, phones, domains = [], [], set()
    all_results = []
    all_subdomains = {}

    is_ip = bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', target))

    # Всегда запускаем nmap для исходного target
    nmap_result = run_nmap_scan(target)

    if is_ip:
        all_results.append({
            'target': target,
            'type': 'ip',
            'nmap': nmap_result
        })
    else:
        target = target.replace("http://", "").replace("https://", "")
        url = f"http://{target}"
        emails, phones = await extract_contacts(url)
        print(f"Найденные телефоны: {phones}")
        print(f"Найденные адреса электронной почты: {emails}")
        domains = set(email.split('@')[1] for email in emails)
        all_domains = list(domains.union({target}))
        for domain in all_domains:
            # Запускаем nmap для каждого домена
            nmap_result = run_nmap_scan(domain)
            gobuster_result = run_gobuster_scan(domain, wordlist)
            subdomains = run_gobuster_subdomains_scan(domain, wordlist)
            all_subdomains[domain] = subdomains
            all_results.append({
                'target': domain,
                'type': 'domain',
                'nmap': nmap_result,
                'gobuster': gobuster_result,
                'subdomains': subdomains
            })
            if subdomains:
                print(f"Найденные субдомены для {domain}: {subdomains}")
        for domain in all_domains:
            subdomains = all_subdomains.get(domain, [])
            for sub in subdomains:
                # Запускаем nmap для каждого субдомена
                nmap_result = run_nmap_scan(sub)
                gobuster_result = run_gobuster_scan(sub, wordlist)
                sub_subdomains = run_gobuster_subdomains_scan(sub, wordlist)
                all_results.append({
                    'target': sub,
                    'type': 'subdomain',
                    'nmap': nmap_result,
                    'gobuster': gobuster_result,
                    'subdomains': sub_subdomains
                })
    try:
        with open('scan_results.txt', 'w', encoding='utf-8') as f:
            f.write("==============================\n")
            f.write(f"SurfaceHarvester Scan Report\n")
            f.write("==============================\n\n")
            f.write(f"Исходная цель: {target}\n\n")
            if not is_ip:
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
        print("Результаты сохранены в scan_results.txt")
    except Exception as e:
        logging.error(f"Ошибка при сохранении отчёта: {e}")
        print(f"Ошибка при сохранении отчёта: {e}")

if __name__ == "__main__":
    asyncio.run(main())