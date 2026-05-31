import urllib.request
import re
import ssl

url = "https://www.ddtown.co.kr/room/105"
ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT@SECLEVEL=1')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8', errors='ignore')
    
    print("Page fetched successfully. Length:", len(html))
    
    # Search for all image extensions in the page
    # Look for anything ending in .jpg, .png, .jpeg
    img_urls = re.findall(r'[\'\"\(]//[^\'\"\)\s]+\.(?:jpg|png|jpeg)', html)
    img_urls += re.findall(r'[\'\"\(]/[^\'\"\)\s]+\.(?:jpg|png|jpeg)', html)
    
    print(f"Found {len(img_urls)} raw image references:")
    unique_imgs = list(set(img_urls))
    for idx, img in enumerate(unique_imgs, 1):
        print(f"  [{idx}] {img}")
        
except Exception as e:
    print("Error:", e)
