import instaloader

def download_all_content(profile, loader):
    print(f"[DOWNLOAD]> Downloading all possible content for @{profile.username}...")
    try:
        loader.download_profile(profile.username, profile_pic_only=True)
        print("    [+] Profile picture downloaded.")

        loader.download_profile(profile.username, profile_pic_only=False)
        print("    [+] Posts downloaded.")

        stories = loader.get_stories(userids=[profile.userid])
        count = 0
        for story in stories:
            for item in story.get_items():
                loader.download_storyitem(item, f"{profile.username}_stories")
                count += 1
        print(f"    [+] {count} story items downloaded." if count else "    [-] No stories available.")

        highlights = loader.get_highlights(profile)
        count = 0
        for highlight in highlights:
            for item in highlight.get_items():
                loader.download_storyitem(item, f"{profile.username}_highlights")
                count += 1
        print(f"    [+] {count} highlight story items downloaded." if count else "    [-] No highlights available.")
    except Exception as e:
        print(f"[ERROR] Download failed: {e}")

def get_instagram_profile_info(username):
    print(f"[INFO]> Info for the user: @{username}\n")

    L = instaloader.Instaloader()
    try:
        profile = instaloader.Profile.from_username(L.context, username)
    except Exception as e:
        print(f"[ERROR] Failed to load the profile : {e}")
        return
    
    print("[*] Profile general info :")
    print(f"    [/] ID                    : {profile.userid}")
    print(f"    [/] complete name         : {profile.full_name}")
    print(f"    [/] username              : {profile.username}")
    print(f"    [/] Biography             : {profile.biography}")
    print(f"    [/] url                   : {profile.external_url}")
    print(f"    [/] verified account      : {'yes' if profile.is_verified else 'no'}")
    print(f"    [/] private account       : {'yes' if profile.is_private else 'no'}")
    print(f"    [/] business account      : {'yes' if profile.is_business_account else 'no'}")

    print("[*] Profile statistics info :")
    print(f"    [/] Followers             : {profile.followers}")
    want_followers = input("[?] you want to see his followers (type 'yes' for see) : ")
    if want_followers == "yes":
        print("    [-] Followers list : ")
        for follower in profile.get_followers():
            print(f"    - @{follower.username}")
    else:
        pass
    print(f"    [/] Followings            : {profile.followees}")
    want_following = input("[?] you want to see his follows (type 'yes' for see) : ")
    if want_following == "yes":
        print("    [-] Followers list : ")
        for following in profile.get_followees():
            print(f"    - @{following.username}")
    else:
        pass
    print(f"    [/] post number           : {profile.mediacount}")
    if profile.mediacount != 0:
        want_analyze = input("[?] you want to analyse the posts (type 'yes' for see) : ")
        if want_analyze == "yes":
            for post in profile.get_posts():
                print("    [-] Post analyse : ")
                print("    - Post publié le :", post.date_utc.strftime("%Y-%m-%d %H:%M:%S"))
                print("    - Caption        :", post.caption[:100] if post.caption else "Aucune")
                print("    - Likes          :", post.likes)
                print("    - Comments       :", post.comments)
                print("    - Hashtags       :", post.caption_hashtags)
                print("    - Mentions       :", post.caption_mentions)
        else:
            pass
    else:
        pass
    
    print("[*] Profile download info : ")
    want_get_pics = input("[?] you want to get the pics of the account (type 'yes' to download) : ")
    if want_get_pics == "yes":
        download_all_content(profile, L)
    else:
        pass

    print("[*] Profile extract info : ")
    want_extract = input("[?] you want ti extract link of the account (type 'yes' for links) : ")

if __name__ == "__main__":
    username = input("[USER]> Username of the instagram account: : ").strip()
    info = get_instagram_profile_info(username)