import requests
import re

def get_instagram_profile_info(username):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR]> error in request : {e}")
        return None
    except ValueError:
       print("[ERROR]> impossible to parse the json file")
       return None
    
    html = response.text

    match = re.search(r'"props"\s*:\s*{\s*"id"\s*:\s*"(\d+)"', html)
    if match:
        ID = match.group(1)
    else:
        print("Non")
        return None

    return ID

if __name__ == "__main__":
    username = input("[USER]> Username of the instagram account: : ").strip()
    info = get_instagram_profile_info(username)