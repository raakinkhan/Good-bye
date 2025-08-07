# video_fetcher, encrypt...
import random
import security_checks
import yt_dlp
import os
import ctypes
from faker import Faker

fake = Faker()
mode = input("Mode- ")
url = input("url- ")
password = input("password- ")
folder = r"C:\Users\AZEEM\Desktop\programs\python\GOOD_BYE\Raw info"
name = f"{fake.word(part_of_speech='noun')}_dos_exec"+str(random.randint(0, 9999))
print(name)

if mode == "direct":
    options = {
        "format": "bestvideo[height<=480]+bestaudio/best[height<=480]",
        'outtmpl':f'{folder}\{name}.%(ext)s',
        'playlist_items': '1',
        "writeinfojson":False,
        "writethumbnail":False,
    }
else:
    options = {
        "format": "best[height<=480]",
        'outtmpl': f'{folder}\{name}.%(ext)s',
        "cookiefile":"x.com_cookies.txt",
        'playlist_items': '1',
        "writeinfojson": False,
        "writethumbnail": False,
    }
    print("check the link, if its externel source before u run...")

def is_twitter_video(info):
    return "url" in info and "video.twimg.com" in info["url"]

with yt_dlp.YoutubeDL(options) as ydl:
    try:
        # Extract info first to check if it’s a Twitter video
        info = ydl.extract_info(url, download=False)
        if is_twitter_video(info):
            print("Fetching Twitter-hosted video...")
            ydl.download([url])
        else:
            print("Not a Twitter-hosted video or externally sourced.")
    except Exception as e:
        for path in os.listdir(r"C:\Users\AZEEM\Desktop\programs\python\GOOD_BYE\Raw info"):
            if os.path.exists(path):
                security_checks.secure_shred(path)
        print(f"Error: {e}")



paths = os.listdir("Raw info/")
try:
    for path in paths:
        ctypes.windll.kernel32.SetFileAttributesW("Raw info/"+path, 0x06)
        security_checks.AES_enc(file_path="Raw info/"+path, password=password)  #raakin
except:
    # kill raw info when interrupted
    print("emergency shred")
    for path in paths:
        security_checks.secure_shred("Raw info/"+path)

