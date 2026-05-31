import urllib.request
import re
import ssl

url = "https://kidsvalley.co.kr/room/739"
ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT@SECLEVEL=1')
headers = {'User-Agent': 'Mozilla/5.0'}

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8', errors='ignore')
    
    print("Page fetched successfully. Length:", len(html))
    
    # Let's search for any image extensions ending in .jpg, .png, .jpeg
    img_urls = re.findall(r'[\'\"\(]//[^\'\"\)\s]+\.(?:jpg|png|jpeg)', html)
    img_urls += re.findall(r'[\'\"\(]/[^\'\"\)\s]+\.(?:jpg|png|jpeg)', html)
    
    print(f"Found {len(img_urls)} image references:")
    unique_imgs = list(set(img_urls))
    for idx, img in enumerate(unique_imgs[:30], 1):
        print(f"  [{idx}] {img}")
        
except Exception as e:
    print("Error:", e)
