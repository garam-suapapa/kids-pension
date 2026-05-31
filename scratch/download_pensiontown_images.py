import os
import re
import urllib.request
import ssl
import time

# Paths
vault_dir = r"F:\pension\Obsidian Vault"
notes_dir = os.path.join(vault_dir, "펜션정리")

pensions_info = [
    {
        "filename": "대부도 펜션타운 피카소.md",
        "id": "105",
        "prefix": "picasso",
        "folder": "대부도 펜션타운 피카소_images",
        "detail_url": "https://www.ddtown.co.kr/room/105"
    },
    {
        "filename": "대부도 펜션타운 모네.md",
        "id": "110",
        "prefix": "monet",
        "folder": "대부도 펜션타운 모네_images",
        "detail_url": "https://www.ddtown.co.kr/room/110"
    },
    {
        "filename": "대부도 펜션타운 아이비.md",
        "id": "200",
        "prefix": "ivy",
        "folder": "대부도 펜션타운 아이비_images",
        "detail_url": "https://www.ddtown.co.kr/room/200"
    }
]

def scrape_and_update():
    ctx = ssl.create_default_context()
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for p in pensions_info:
        filename = p["filename"]
        room_id = p["id"]
        prefix = p["prefix"]
        folder_name = p["folder"]
        detail_url = p["detail_url"]
        
        file_path = os.path.join(notes_dir, filename)
        if not os.path.exists(file_path):
            print(f"Skipping {filename} (note file not found)")
            continue
            
        print(f"\n================ Scrape room {room_id} ({filename}) ================")
        
        # 1. Fetch Room Detail Page HTML
        try:
            req = urllib.request.Request(detail_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as response:
                html = response.read().decode('utf-8', errors='ignore')
            print(f"Fetched detail page. Length: {len(html)}")
        except Exception as e:
            print(f"Error fetching page for room {room_id}: {e}")
            continue
            
        # 2. Extract image URLs
        # Matching pattern: //img2.itravelgo.co.kr/data/pension/ID/floor/...jpg or landscape/...jpg
        pattern_floor = rf'//img2\.itravelgo\.co\.kr/data/pension/{room_id}/floor/[^\s\'\"\)]+\.jpg'
        pattern_land = rf'//img2\.itravelgo\.co\.kr/data/pension/{room_id}/landscape/[^\s\'\"\)]+\.jpg'
        
        img_urls = re.findall(pattern_floor, html) + re.findall(pattern_land, html)
        img_urls = list(set(img_urls))
        print(f"Found {len(img_urls)} unique image references.")
        
        # Prefer high-res "/1920/" or "/1024/" URLs if they exist
        high_res_urls = []
        for img in img_urls:
            # If the URL already contains a size subdirectory, keep it or normalize it to high-res /1920/
            # For example: data/pension/105/floor/307/phpTBEtVQ.jpg -> can it be normalized to /1920/phpTBEtVQ.jpg?
            # Let's see: the script output shows '//img2.itravelgo.co.kr/data/pension/105/floor/307/1920/phpnATuse.jpg'
            # So some images have 1920 in their path.
            if '/1920/' in img:
                high_res_urls.append(img)
            elif '/1024/' in img:
                # convert /1024/ to /1920/ if possible, or keep it
                high_res_urls.append(img)
                
        # If no explicit 1920/1024 images, try to see if we can convert generic floor images to 1920
        if len(high_res_urls) < 4:
            for img in img_urls:
                if img not in high_res_urls:
                    # e.g. //img2.itravelgo.co.kr/data/pension/105/floor/307/phpBLdLYb.jpg
                    # Let's try to inject /1920/ before the filename
                    parts = img.split('/')
                    if len(parts) >= 2 and not parts[-2].isdigit(): # if second to last part is not a number like 1920
                        filename_part = parts[-1]
                        folder_parts = parts[:-1]
                        new_img_url = "/".join(folder_parts) + "/1920/" + filename_part
                        if new_img_url not in high_res_urls:
                            high_res_urls.append(new_img_url)
                            
        # If still empty, use raw img_urls
        if not high_res_urls:
            high_res_urls = img_urls
            
        high_res_urls = list(set(high_res_urls))
        print(f"Selected {len(high_res_urls)} candidate high-res URLs.")
        
        # 3. Create destination folder
        room_img_dir = os.path.join(vault_dir, folder_name)
        os.makedirs(room_img_dir, exist_ok=True)
        
        # 4. Download up to 6 images
        downloaded_images = []
        download_count = 0
        for idx, img_url in enumerate(high_res_urls):
            if download_count >= 6:
                break
                
            full_url = "https:" + img_url if img_url.startswith("//") else img_url
            if not full_url.startswith("http"):
                full_url = "https://" + img_url
                
            img_filename = f"{prefix}_room_{download_count + 1}.jpg"
            dest_path = os.path.join(room_img_dir, img_filename)
            
            try:
                # Try downloading high-res
                req_file = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(req_file, context=ctx) as src, open(dest_path, "wb") as dest:
                    dest.write(src.read())
                print(f"  Downloaded: {img_filename} from {full_url}")
                downloaded_images.append(img_filename)
                download_count += 1
            except Exception as e:
                # Fallback to the original URL if we tried to inject /1920/ and it failed
                if '/1920/' in full_url:
                    fallback_url = full_url.replace('/1920/', '/')
                    try:
                        req_file = urllib.request.Request(fallback_url, headers=headers)
                        with urllib.request.urlopen(req_file, context=ctx) as src, open(dest_path, "wb") as dest:
                            dest.write(src.read())
                        print(f"  Downloaded Fallback: {img_filename} from {fallback_url}")
                        downloaded_images.append(img_filename)
                        download_count += 1
                    except Exception as e_fb:
                        print(f"  Failed fallback download for {fallback_url}: {e_fb}")
                else:
                    print(f"  Failed download for {full_url}: {e}")
                    
            time.sleep(0.1) # politeness delay
            
        # 5. Update the markdown note (replace old links, update reservation URL)
        if downloaded_images:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Clean up old image links ![[...]]
            content = re.sub(r'!\[\[[^\]]+\]\]\n?', '', content)
            
            # Update Link in metadata to point to ddtown detail page
            content = re.sub(
                r'(-\s*\*\*링크\*\*:\s*)(.*)',
                f'\\g<1>{detail_url}',
                content
            )
            
            # Prepend new image links
            img_links = "\n".join(f"![[{img}]]" for img in downloaded_images)
            new_content = img_links + "\n\n" + content.strip()
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            print(f"Successfully updated {filename} with {len(downloaded_images)} images and link: {detail_url}")
            
if __name__ == "__main__":
    scrape_and_update()
