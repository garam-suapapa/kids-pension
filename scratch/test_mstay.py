import urllib.request
import ssl
import re

url = "https://ddpension3.mstay.co.kr/m_member/index.html?gn=&rgn=&year=2026&month=05&day=30"
ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT@SECLEVEL=1')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8', errors='ignore')
    print("Page fetched successfully. Length:", len(html))
    
    # Let's search for any occurrence of "피카소", "모네", "마네", "아이비"
    names = ["피카소", "모네", "마네", "아이비", "Picasso", "Monet", "Ivy", "Picasso", "Mane"]
    for name in names:
        if name in html:
            print(f"Found keyword '{name}' in index.html!")
            
    # Find all iframes
    iframes = re.findall(r'<iframe[^>]+src=["\']([^"\']+)["\']', html)
    print("Iframes:", iframes)
    
    # Find scripts
    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\']', html)
    print("Scripts:", scripts[:10])
    
    # Find all links
    links = re.findall(r'href=["\']([^"\']+)["\']', html)
    print("Links (first 30):", links[:30])
    
except Exception as e:
    print("Error:", e)
