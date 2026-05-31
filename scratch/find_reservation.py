import urllib.request
import re
import ssl

url = "http://www.ddtown.co.kr"
ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT@SECLEVEL=1')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8', errors='ignore')
    
    print("Fetched ddtown homepage. Length:", len(html))
    
    # Extract all links (hrefs)
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html)
    print("Found Hrefs:")
    for href in hrefs:
        if 'reservation' in href or 'room' in href or 'reserve' in href or 'sub' in href or 'mstay' in href:
            print("  ", href)
            
except Exception as e:
    print("Error:", e)
