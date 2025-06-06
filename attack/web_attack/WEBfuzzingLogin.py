import requests
import argparse
import os

parser = argparse.ArgumentParser(description="Simple web fuzzer for login pages")
parser.add_argument("--url", required=True, help="Base URL (e.g., https://example.com/)")
parser.add_argument("--file", required=True, help="Path to the login wordlist")

args = parser.parse_args()
url = args.url
fichier = args.file

if not os.path.isfile(fichier):
    print(f"[!] Le fichier '{fichier}' n'existe pas.")
    exit(1)

if not url.endswith("/"):
    url += "/"

with open(fichier, "r") as login_pages:
    for login_page in login_pages:
        login_page = login_page.strip()
        full_url = url + login_page
        print(f"[?] Checking {full_url}...")
        try:
            response = requests.get(full_url, timeout=5)
            if response.status_code == 200:
                print(f"[+] Login resource detected at: {full_url}")
            else:
                print(f"[-] {full_url} -> HTTP {response.status_code}")
        except requests.RequestException as e:
            print(f"[!] Error while checking {full_url}: {e}")