import requests
from bs4 import BeautifulSoup
import hashlib

error_template = {}

def get_error_signature(site, url_template, headers):
    fake_username = "thisisashittyfckusernamewhodoesntexistemdrrazdihTfYeuOdgeFlEEjgLxnOfdi"
    url = url_template.format(username=fake_username)
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            return extract_signature(soup, site)
    except:
        pass
    return None

def extract_signature(soup, site):
    signature_elements = []

    site_selectors = {
        "Facebook": ["title", "meta[property='og:title']", ".error", "#content"],
        "X": ["title", "main", ".error-text", "[data-testid='error']"],
        "Instagram": ["title", "meta[property='og:title']", ".error-container", "main"],
        "TikTok": ["title", "[data-e2e='user-title']", ".error", "main"],
        "Snapchat": ["title", ".error", "main", "h1"],
        "Reddit": ["title", ".error", "h3", ".titlebox"],
        "YouTube": ["title", "meta[property='og:title']", ".error", "#content"],
        "SoundCloud": ["title", ".error", ".header", "main"],
        "GitHub": ["title", ".error", ".blankslate", "main"],
        "GitLab": ["title", ".error", ".blank-state", "main"],
        "Steam": ["title", ".error", ".profile_page", "main"],
        "Twitch": ["title", ".error", "[data-test-selector='user-display-name']", "main"],
        "Roblox": ["title", ".error", ".profile-header", "main"],
        "Fiverr": ["title", ".error", ".user-profile", "main"],
        "Patreon": ["title", ".error", "[data-tag='user-name']", "main"],
        "Shopify": ["title", ".error", ".site-header", "main"],
        "Pinterest": ["title", ".error", "[data-test-id='user-name']", "main"],
        "Quora": ["title", ".error", ".user_profile", "main"],
        "Myspace": ["title", ".error", ".profile", "main"]
    }

    selectors = site_selectors.get(site, ["title", ".error", "h1", "h2", "main"])

    for selector in selectors:
        elements = soup.select(selector)
        for element in elements:
            if element:
                text = element.get_text(strip=True)[:200]
                if text:
                    signature_elements.append(text)
                if element.get("content"):
                    signature_elements.append(element.get("content")[:100])
                break

    if signature_elements:
        combined = "|".join(signature_elements)
        return hashlib.md5(combined.encode()).hexdigest()
    
    return None

def is_error_page(site, html, final_url):
    try:
        error_sig = error_template.get(site)
        if not error_sig:
            print(f"[!] Error of signature from : {site}")
            return False

        soup = BeautifulSoup(html, "html.parser")
        current_sig = extract_signature(soup, site)
        if not current_sig:
            return False
        
        return current_sig == error_sig
    except Exception as e:
        print(f"[!] Error from the analyse : {e}")
        return False

def real_user(site, html, final_url):
    return not is_error_page(site, html, final_url)

def check_username(username):
    sites = {
        "Facebook": f"https://www.facebook.com/{username}",
        "X": f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Snapchat": f"https://www.snapchat.com/add/{username}",
        "Reddit": f"https://www.reddit.com/user/{username}/",
        "YouTube": f"https://www.youtube.com/@{username}",
        "SoundCloud": f"https://soundcloud.com/{username}",
        "GitHub": f"https://github.com/{username}",
        "GitLab": f"https://gitlab.com/{username}",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Roblox": f"https://www.roblox.com/fr/users/{username}/profile?friendshipSourceType=PlayerSearch",
        "Fiverr": f"https://www.fiverr.com/{username}",
        "Patreon": f"https://www.patreon.com/{username}",
        "Shopify": f"https://{username}.myshopify.com/",
        "Pinterest": f"https://www.pinterest.com/{username}/",
        "Quora": f"https://www.quora.com/profile/{username}",
        "Myspace": f"https://myspace.com/{username}",
    }

    headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9"
    }
    
    print("\n[.] Generation of the error link, wait 10 sec ...\n")

    for site, url_templates in sites.items():
        print(f"[.] analyse of {site}")
        error_template[site] = get_error_signature(site, url_templates, headers)
        if not error_template:
            print(f"[!] Failure of signature generation for {site}")


    print(f"\n[*] Result for '{username}' : \n")
    
    for site, url_templates in sites.items():
        if url_templates is None:
            continue
        url = url_templates.format(username=username)
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                if real_user(site, response.text, response.url):
                    print(f"[+]> {site} : {url} | HTTP : {response.status_code}")
                else:
                    print(f"[~]> {site} : {url} | HTTP : {response.status_code}")
            elif response.status_code in [301, 302]:
                print(f"[=]> {site} : {url} | HTTP : {response.status_code}")
            else:
                print(f"[-]> {site} : {url} | HTTP : {response.status_code}")
        except requests.RequestException as e:
            print(f"[!] Request problem : {e}")
            continue
    
if __name__ == "__main__":
    username = input("[@]> Username to found : ").strip()
    check_username(username)