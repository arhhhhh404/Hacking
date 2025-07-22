import requests

def check_username(username):
    sites = {
        "Facebook": f"https://www.facebook.com/{username}",
        "X": f"https://twitter.com/{username}",
        "Instagram": f"https://www.instagram.com/{username}/",
        "TikTok": f"https://www.tiktok.com/@{username}",
        "Snapchat": f"https://www.snapchat.com/add/{username}",
        "Tumblr": f"https://{username}.tumblr.com/",
        "Reddit": f"https://www.reddit.com/user/{username}/",
        "Mastodon": f"https://mastodon.social/@{username}",
        "Weibo": f"https://weibo.com/{username}",
        "YouTube": f"https://www.youtube.com/@{username}",
        "DeviantArt": f"https://www.deviantart.com/{username}",
        "Behance": f"https://www.behance.net/{username}",
        "Dribbble": f"https://dribbble.com/{username}",
        "Flickr": f"https://www.flickr.com/people/{username}",
        "SoundCloud": f"https://soundcloud.com/{username}",
        "Dailymotion": f"https://www.dailymotion.com/{username}",
        "Mix": f"https://mix.com/{username}",
        "GitHub": f"https://github.com/{username}",
        "GitLab": f"https://gitlab.com/{username}",
        "Bitbucket": f"https://bitbucket.org/{username}",
        "StackOverflow": f"https://stackoverflow.com/users/{username}",
        "CodePen": f"https://codepen.io/{username}",
        "Medium": f"https://{username}.medium.com/",
        "Blogspot": f"https://{username}.blogspot.com/",
        "WordPress.com": f"https://{username}.wordpress.com/",
        "Tumblr": f"https://{username}.tumblr.com/",
        "Steam": f"https://steamcommunity.com/id/{username}",
        "Twitch": f"https://www.twitch.tv/{username}",
        "Roblox": f"https://www.roblox.com/users/{username}/profile",
        "PlayStation Network": f"https://my.playstation.com/{username}",
        "Xbox Live": f"https://account.xbox.com/en-us/Profile?gamertag={username}",
        "Discord": None,
        "Mixer": f"https://mixer.com/{username}",
        "Etsy": f"https://www.etsy.com/shop/{username}",
        "Fiverr": f"https://www.fiverr.com/{username}",
        "Patreon": f"https://www.patreon.com/{username}",
        "BuyMeACoffee": f"https://www.buymeacoffee.com/{username}",
        "Shopify": f"https://{username}.myshopify.com/",
        "Pinterest": f"https://www.pinterest.com/{username}/",
        "500px": f"https://500px.com/{username}",
        "Kinja": f"https://{username}.kinja.com/",
        "Foursquare": f"https://foursquare.com/user/{username}",
        "PayPal": None,
        "Cash App": None,
        "Venmo": f"https://venmo.com/{username}",
        "Quora": f"https://www.quora.com/profile/{username}",
        "Goodreads": f"https://www.goodreads.com/user/show/{username}",
        "LiveJournal": f"https://{username}.livejournal.com/",
        "Myspace": f"https://myspace.com/{username}",
        "Slashdot": f"https://slashdot.org/~{username}",
        "Couchsurfing": f"https://www.couchsurfing.com/people/{username}",
        "Ravelry": f"https://www.ravelry.com/people/{username}",
        "Slack": None,
        "Trello": f"https://trello.com/{username}",
        "IFTTT": f"https://ifttt.com/p/{username}",
        "NameChecker": f"https://namechecker.org/profile/{username}",
        "CheckUserNames": f"https://checkusernames.com/user/{username}",
        "Knowem": f"https://knowem.com/u/{username}"
    }

    headers = {
       "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36" 
    }
    
    print(f"\n[*] Result for '{username}' : \n")
    
    for site, url_templates in sites.items():
        if url_templates is None:
            continue
        url = url_templates.format(username=username)
        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                print(f"[+]> {site} : {url} | HTTP : {response.status_code}")
            elif  response.status_code == 301 or 302:
                print(f"[~]> {site} : {url} | HTTP : {response.status_code}")
            else:
                print(f"[-]> {site} : {url} | HTTP : {response.status_code}")
        except requests.RequestException as e:
            print("[!] Request problem : {e}")
            continue
    
if __name__ == "__main__":
    username = input("[@]> Username to found : ").strip()
    check_username(username)