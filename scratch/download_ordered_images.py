import os
import re
import urllib.request
import ssl
import time
import shutil

# Paths
vault_dir = r"F:\pension\Obsidian Vault"
notes_dir = os.path.join(vault_dir, "펜션정리")
assets_dir = r"F:\pension\assets\pension_images"

# Target pensions list
pensions_list = [
    # 7 Kids Valley
    {"filename": "대부도 키즈밸리 하이베어.md", "id": "328", "prefix": "room_328", "folder": "대부도 키즈밸리 하이베어_images", "url": "https://kidsvalley.co.kr/room/328"},
    {"filename": "대부도 키즈밸리 가봄.md", "id": "709", "prefix": "room_709", "folder": "대부도 키즈밸리 가봄_images", "url": "https://kidsvalley.co.kr/room/709"},
    {"filename": "대부도 키즈밸리 달빛되어.md", "id": "828", "prefix": "room_828", "folder": "대부도 키즈밸리 달빛되어_images", "url": "https://kidsvalley.co.kr/room/828"},
    {"filename": "대부도 키즈밸리 꾸꾸.md", "id": "789", "prefix": "room_789", "folder": "대부도 키즈밸리 꾸꾸_images", "url": "https://kidsvalley.co.kr/room/789"},
    {"filename": "대부도 키즈밸리 더데이.md", "id": "337", "prefix": "room_337", "folder": "대부도 키즈밸리 더데이_images", "url": "https://kidsvalley.co.kr/room/337"},
    {"filename": "대부도 키즈밸리 골든웨이브.md", "id": "739", "prefix": "goldenwave", "folder": "대부도 키즈밸리 골든웨이브_images", "url": "https://kidsvalley.co.kr/room/739"},
    {"filename": "대부도 키즈밸리 더킹.md", "id": "740", "prefix": "room_740", "folder": "대부도 키즈밸리 더킹_images", "url": "https://kidsvalley.co.kr/room/740"},
    # 3 Pension Town
    {"filename": "대부도 펜션타운 피카소.md", "id": "105", "prefix": "picasso", "folder": "대부도 펜션타운 피카소_images", "url": "https://www.ddtown.co.kr/room/105"},
    {"filename": "대부도 펜션타운 모네.md", "id": "110", "prefix": "monet", "folder": "대부도 펜션타운 모네_images", "url": "https://www.ddtown.co.kr/room/110"},
    {"filename": "대부도 펜션타운 아이비.md", "id": "200", "prefix": "ivy", "folder": "대부도 펜션타운 아이비_images", "url": "https://www.ddtown.co.kr/room/200"}
]

def scrape_ordered_photos():
    ctx = ssl.create_default_context()
    ctx.set_ciphers('DEFAULT@SECLEVEL=1')
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for pension in pensions_list:
        filename = pension["filename"]
        room_id = pension["id"]
        prefix = pension["prefix"]
        folder_name = pension["folder"]
        detail_url = pension["url"]
        
        file_path = os.path.join(notes_dir, filename)
        if not os.path.exists(file_path):
            print(f"Skipping {filename} (note file not found)")
            continue
            
        print(f"\n================ Scrape room {room_id} ({filename}) (ORDERED) ================")
        
        # 1. Fetch Page HTML
        try:
            req = urllib.request.Request(detail_url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as response:
                html = response.read().decode('utf-8', errors='ignore')
            print(f"Fetched page. Length: {len(html)}")
        except Exception as e:
            print(f"Error fetching page for room {room_id}: {e}")
            continue
            
        # 2. Extract image URLs
        # We find both floor and landscape patterns depending on site
        pattern_floor = rf'//img2\.itravelgo\.co\.kr/data/pension/{room_id}/floor/[^\s\'\"\)]+\.jpg'
        pattern_land = rf'//img2\.itravelgo\.co\.kr/data/pension/{room_id}/landscape/[^\s\'\"\)]+\.jpg'
        
        # We do re.finditer to extract in their exact order of appearance in HTML
        all_matches = []
        for match in re.finditer(pattern_floor, html):
            all_matches.append((match.start(), match.group(0)))
        for match in re.finditer(pattern_land, html):
            all_matches.append((match.start(), match.group(0)))
            
        # Sort by match starting position to strictly preserve HTML order
        all_matches.sort(key=lambda x: x[0])
        raw_urls = [m[1] for m in all_matches]
        
        # Deduplicate while preserving order
        seen_urls = set()
        ordered_urls = []
        for url in raw_urls:
            # We normalize high-res if needed, but let's first check if there are 1920/1024
            # Keep original structure as fallback
            if url not in seen_urls:
                seen_urls.add(url)
                ordered_urls.append(url)
                
        print(f"Found {len(ordered_urls)} unique ordered images in HTML.")
        
        # 3. Filter/Prefer High-Res versions but preserve order!
        high_res_ordered = []
        for img in ordered_urls:
            # Check if there is already a sized subdirectory or inject it if possible
            # Sized versions: /1920/ or /1024/
            if '/1920/' in img:
                high_res_ordered.append(img)
            elif '/1024/' in img:
                high_res_ordered.append(img)
            else:
                # Try to inject /1920/ to get the high resolution version
                parts = img.split('/')
                if len(parts) >= 2 and not parts[-2].isdigit():
                    filename_part = parts[-1]
                    folder_parts = parts[:-1]
                    injected = "/".join(folder_parts) + "/1920/" + filename_part
                    if injected not in high_res_ordered:
                        high_res_ordered.append(injected)
                else:
                    if img not in high_res_ordered:
                        high_res_ordered.append(img)
                        
        # Deduplicate high_res list while keeping order
        seen_hr = set()
        final_download_urls = []
        for url in high_res_ordered:
            if url not in seen_hr:
                seen_hr.add(url)
                final_download_urls.append(url)
                
        # If still very few, fallback to ordered_urls
        if len(final_download_urls) < 4:
            final_download_urls = ordered_urls
            
        print(f"Selected {len(final_download_urls)} candidate high-res ordered URLs.")
        
        # 4. Create/Clean destination folder
        room_img_dir = os.path.join(vault_dir, folder_name)
        if os.path.exists(room_img_dir):
            shutil.rmtree(room_img_dir)
        os.makedirs(room_img_dir, exist_ok=True)
        
        # 5. Download up to 8 images to perfectly map all criteria
        downloaded_images = []
        download_count = 0
        for idx, img_url in enumerate(final_download_urls):
            if download_count >= 8:
                break
                
            full_url = "https:" + img_url if img_url.startswith("//") else img_url
            if not full_url.startswith("http"):
                full_url = "https://" + img_url
                
            img_filename = f"{prefix}_room_{download_count + 1}.jpg"
            dest_path = os.path.join(room_img_dir, img_filename)
            
            try:
                req_file = urllib.request.Request(full_url, headers=headers)
                with urllib.request.urlopen(req_file, context=ctx) as src, open(dest_path, "wb") as dest:
                    dest.write(src.read())
                print(f"  [{download_count+1}] Downloaded: {img_filename} from {full_url}")
                downloaded_images.append(img_filename)
                download_count += 1
            except Exception as e:
                # If explicit sizing failed, fallback by stripping it
                if '/1920/' in full_url:
                    fallback_url = full_url.replace('/1920/', '/')
                    try:
                        req_file = urllib.request.Request(fallback_url, headers=headers)
                        with urllib.request.urlopen(req_file, context=ctx) as src, open(dest_path, "wb") as dest:
                            dest.write(src.read())
                        print(f"  [{download_count+1}] Downloaded Fallback: {img_filename} from {fallback_url}")
                        downloaded_images.append(img_filename)
                        download_count += 1
                    except Exception as e_fb:
                        # try 1024
                        fallback_url_2 = full_url.replace('/1920/', '/1024/')
                        try:
                            req_file = urllib.request.Request(fallback_url_2, headers=headers)
                            with urllib.request.urlopen(req_file, context=ctx) as src, open(dest_path, "wb") as dest:
                                dest.write(src.read())
                            print(f"  [{download_count+1}] Downloaded Fallback 1024: {img_filename} from {fallback_url_2}")
                            downloaded_images.append(img_filename)
                            download_count += 1
                        except:
                            print(f"  Failed download for {full_url}: {e_fb}")
                else:
                    print(f"  Failed download for {full_url}: {e}")
                    
            time.sleep(0.1)
            
        # 6. Update markdown note with perfectly ordered photo links
        if downloaded_images:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Clean old links
            content = re.sub(r'!\[\[[^\]]+\]\]\n?', '', content)
            
            # Update Link in metadata to point to detail page (for kids valley as well!)
            content = re.sub(
                r'(-\s*\*\*링크\*\*:\s*)(.*)',
                f'\\g<1>{detail_url}',
                content
            )
            
            # Prepend new links in original order
            img_links = "\n".join(f"![[{img}]]" for img in downloaded_images)
            new_content = img_links + "\n\n" + content.strip()
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
                
            print(f"Successfully updated {filename} with {len(downloaded_images)} ordered images!")
            
if __name__ == "__main__":
    scrape_ordered_photos()
