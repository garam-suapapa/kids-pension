import urllib.request
import re
import ssl

url = "https://www.ddtown.co.kr/room"
ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT@SECLEVEL=1')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8', errors='ignore')
    
    print("HTML length:", len(html))
    
    # We want to find all objects inside the javascript array.
    # Usually they look like:
    # {
    #     id:'...',
    #     title:'...',
    #     content:'...'
    # }
    
    # Let's search for patterns like id:'\d+', title:'[^']+'
    pattern = r"id\s*:\s*['\"](\d+)['\"]\s*,\s*title\s*:\s*['\"]([^'\"]+)['\"]"
    matches = re.findall(pattern, html)
    print(f"Found {len(matches)} room entries:")
    for idx, (room_id, room_title) in enumerate(matches, 1):
        print(f"[{idx}] ID: {room_id} -> Title: {room_title}")
        
except Exception as e:
    print("Error:", e)
