import os
import re
import urllib.request
import ssl
import time

vault_dir = r"F:\pension\Obsidian Vault"
notes_dir = os.path.join(vault_dir, "펜션정리")
filename = "대부도 키즈밸리 골든웨이브.md"
room_id = "739"
folder_name = "대부도 키즈밸리 골든웨이브_images"
url = f"https://kidsvalley.co.kr/room/{room_id}"

ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT@SECLEVEL=1')
headers = {'User-Agent': 'Mozilla/5.0'}

file_path = os.path.join(notes_dir, filename)
if not os.path.exists(file_path):
    print(f"Error: {filename} not found.")
    exit(1)

try:
    print(f"Fetching Golden Wave page from {url}...")
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8', errors='ignore')
    
    print("Page fetched. Parsing images...")
    
    # Extract any image references matching the pension 739 CDN path
    pattern_floor = rf'//img2\.itravelgo\.co\.kr/data/pension/{room_id}/floor/[^\s\'\"\)]+\.jpg'
    pattern_land = rf'//img2\.itravelgo\.co\.kr/data/pension/{room_id}/landscape/[^\s\'\"\)]+\.jpg'
    
    img_urls = re.findall(pattern_floor, html) + re.findall(pattern_land, html)
    img_urls = list(set(img_urls))
    print(f"Found {len(img_urls)} unique image references.")
    
    # Prefer high-res "/1024/" or "/1920/" if they exist
    high_res_urls = []
    for img in img_urls:
        if '/1920/' in img:
            high_res_urls.append(img)
        elif '/1024/' in img:
            high_res_urls.append(img)
            
    # Try normalizing remaining floor paths if we need more images
    if len(high_res_urls) < 6:
        for img in img_urls:
            if img not in high_res_urls:
                high_res_urls.append(img)
                
    high_res_urls = list(set(high_res_urls))
    print(f"Selected {len(high_res_urls)} candidate image URLs.")
    
    # Create directory
    dest_dir = os.path.join(vault_dir, folder_name)
    os.makedirs(dest_dir, exist_ok=True)
    
    # Download up to 6 images
    downloaded_images = []
    download_count = 0
    for idx, img_url in enumerate(high_res_urls):
        if download_count >= 6:
            break
            
        full_url = "https:" + img_url if img_url.startswith("//") else img_url
        if not full_url.startswith("http"):
            full_url = "https://" + img_url
            
        img_filename = f"goldenwave_room_{download_count + 1}.jpg"
        dest_path = os.path.join(dest_dir, img_filename)
        
        try:
            print(f"Downloading [{download_count+1}/6]: {img_filename} from {full_url}")
            req_file = urllib.request.Request(full_url, headers=headers)
            with urllib.request.urlopen(req_file, context=ctx) as src, open(dest_path, "wb") as dest:
                dest.write(src.read())
            downloaded_images.append(img_filename)
            download_count += 1
        except Exception as e:
            # If explicit 1024/1920 failed, try fallback by stripping size subdirectory
            if '/1024/' in full_url:
                fallback = full_url.replace('/1024/', '/')
                try:
                    print(f"  Trying fallback for {img_filename} from {fallback}")
                    req_fb = urllib.request.Request(fallback, headers=headers)
                    with urllib.request.urlopen(req_fb, context=ctx) as src, open(dest_path, "wb") as dest:
                        dest.write(src.read())
                    downloaded_images.append(img_filename)
                    download_count += 1
                except Exception as ef:
                    print(f"  Fallback failed: {ef}")
            else:
                print(f"  Download failed: {e}")
                
        time.sleep(0.1)
        
    if downloaded_images:
        print(f"Downloaded {len(downloaded_images)} images successfully!")
        
        # Read note
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Strip any old links if they exist (just to be clean)
        content = re.sub(r'!\[\[[^\]]+\]\]\n?', '', content)
        
        # Prepend new image links
        img_links = "\n".join(f"![[{img}]]" for img in downloaded_images)
        new_content = img_links + "\n\n" + content.strip()
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        print(f"Successfully updated note {filename} with the photo links!")
        
except Exception as e:
    print("Scraping error:", e)
