import requests

def get_instagram_profile_info(username, sessionid):
    url = f"https://www.instagram.com/{username}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "X-IG-App-ID": "936619743392459"
    }

    cookies = {
        "sessionid": sessionid
    }

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"[ERROR]> error in request : {e}")
        return None
    except ValueError:
       print("[ERROR]> impossible to parse the json file")
       return None
    
    user = data.get("data", ()).get("user")
    if not user:
        print("[ERROR]> no userdata found")
        return None 

    profile_info = {
        "id": user["id"],
        "username": user["username"],
        "full_name": user["full_name"],
        "biography": user["biography"],
        "profile_pic_url": user["profile_pic_url_hd"],
        "is_private": user["is_private"],
        "is_verified": user["is_verified"],
        "followers": user["edge_followed_by"]["count"],
        "following": user["edge_follow"]["count"],
        "posts_count": user["edge_owner_to_timeline_media"]["count"],
        "external_url": user["external_url"],
        "category": user.get("category_name"),
        "business": user.get("is_business_account"),
    }

    return profile_info

if __name__ == "__main__":
    username = input("[USER]> Username of the instagram account: : ").strip()
    session = input("[SESSION]> Cookie sessionid (from your navigator: open inspector -> Application -> Cookies -> instagram.com) : ")
    info = get_instagram_profile_info(username, session)

    if info:
        print("[INFO]> Profile info : ")
        for key, value in info.items():
            print(f"{key} : {value}")