import urllib.request
import json
import re
import sys

video_url = sys.argv[1] if len(sys.argv) > 1 else "https://youtu.be/VIwe0zJQiTA"
match = re.search(r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})', video_url)
vid = match.group(1) if match else None

print(f"[*] Testing Video ID: {vid}")

# Test direct extract
api = f"https://api.allorigins.win/get?url=https://www.youtube.com/watch?v={vid}"
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    req = urllib.request.Request(f"https://pipedapi.kavin.rocks/streams/{vid}", headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode())
        streams = data.get("videoStreams", [])
        if streams:
            print("[+] SUCCESS! Work kar raha hai.")
            print(f"Title: {data.get('title')}")
            print(f"Direct Link: {streams[0].get('url')[:60]}...")
        else:
            print("[-] Direct streams nahi mile.")
except Exception as e:
    print(f"[*] Fallback test running...")
    try:
        req2 = urllib.request.Request(f"https://api.vkrdownloader.workers.dev/server?v=https://youtu.be/{vid}", headers=headers)
        with urllib.request.urlopen(req2, timeout=10) as r2:
            data2 = json.loads(r2.read().decode())
            if data2.get("data") and data2["data"].get("downloads"):
                print("[+] SUCCESS! Work kar raha hai.")
                print(f"Title: {data2['data'].get('title')}")
                print("Download Link Ready!")
            else:
                print("[-] Error in extraction:", data2)
    except Exception as err:
        print("[-] Test failed:", err)
