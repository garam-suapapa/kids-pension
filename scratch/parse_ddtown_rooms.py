import urllib.request
import re
import ssl

ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT@SECLEVEL=1')
headers = {'User-Agent': 'Mozilla/5.0'}

urls = [
    "https://www.ddtown.co.kr/room",
    "https://www.ddtown.co.kr/room/first",
    "https://www.ddtown.co.kr/room/second"
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        print(f"\n--- URL: {url} (Length: {len(html)}) ---")
        
        # Look for keywords
        keywords = ["피카소", "모네", "마네", "아이비", "picasso", "monet", "mane", "ivy"]
        for kw in keywords:
            matches = list(re.finditer(kw, html, re.IGNORECASE))
            if matches:
                print(f"Found keyword '{kw}' {len(matches)} times!")
                # Print around the first match
                first_idx = matches[0].start()
                start = max(0, first_idx - 100)
                end = min(len(html), first_idx + 300)
                print(f"Context: {html[start:end]}\n")
                
    except Exception as e:
        print(f"Error fetching {url}: {e}")
