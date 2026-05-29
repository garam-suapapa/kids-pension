import os
import re
import shutil
import json

# Paths
vault_dir = r"F:\pension\Obsidian Vault"
notes_dir = os.path.join(vault_dir, "펜션정리")
assets_dir = r"F:\pension\assets\pension_images"
output_js_path = r"F:\pension\pensions_data.js"

# Create assets folder
os.makedirs(assets_dir, exist_ok=True)

# Helper to find file in vault recursively
def find_image_file(filename):
    for root, dirs, files in os.walk(vault_dir):
        if filename in files:
            return os.path.join(root, filename)
    return None

def parse_metadata_line(line):
    # Match "- **Key**: Value" or "- **Key**:Value"
    match = re.match(r'-\s*\*\*([^*]+)\*\*:\s*(.*)', line.strip())
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None

def parse_pension_note(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Get filename without extension as fallback name
    file_basename = os.path.basename(file_path)
    fallback_name = os.path.splitext(file_basename)[0]

    # Find the title (first H1)
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    name = title_match.group(1).strip() if title_match else fallback_name

    # Initialize data structure
    pension_data = {
        "id": re.sub(r'[^a-zA-Z0-9가-힣]', '_', fallback_name),
        "name": name,
        "filename": file_basename,
        "metadata": {
            "온수풀": "확인 필요",
            "방개수": 0,
            "금액": "확인 필요",
            "금액숫자": 999, # fallback for sorting
            "키즈풀빌라": "아니오",
            "대중교통": "확인 필요",
            "평점": 4.5,
            "링크": "#"
        },
        "kids_facilities": [],
        "general_facilities": [],
        "pros": [],
        "cons": [],
        "memo": "",
        "images": []
    }

    # Split into sections by H2
    sections = re.split(r'^##\s+', content, flags=re.MULTILINE)
    
    # First section contains metadata if there is any text before the first H2
    for section in sections:
        lines = [l.strip() for l in section.split('\n') if l.strip()]
        if not lines:
            continue
            
        header = lines[0]
        section_content = lines[1:]

        # 1. Metadata Section
        if "평가 기준" in header or header.startswith("[평가"):
            for line in section_content:
                meta = parse_metadata_line(line)
                if meta:
                    key, val = meta
                    if "온수풀" in key:
                        pension_data["metadata"]["온수풀"] = val
                    elif "방" in key:
                        pension_data["metadata"]["방개수"] = val
                        # Extract digits
                        digits = re.findall(r'\d+', val)
                        if digits:
                            pension_data["metadata"]["방개수_숫자"] = int(digits[0])
                        else:
                            pension_data["metadata"]["방개수_숫자"] = 0
                    elif "금액" in key or "가격" in key:
                        pension_data["metadata"]["금액"] = val
                        # Parse out primary price digit (e.g. 85만원 -> 85)
                        price_digits = re.findall(r'\d+', val)
                        if price_digits:
                            pension_data["metadata"]["금액숫자"] = int(price_digits[0])
                    elif "키즈" in key:
                        pension_data["metadata"]["키즈풀빌라"] = val
                    elif "대중교통" in key:
                        pension_data["metadata"]["대중교통"] = val
                    elif "평점" in key:
                        try:
                            pension_data["metadata"]["평점"] = float(re.findall(r'\d+\.\d+|\d+', val)[0])
                        except:
                            pension_data["metadata"]["평점"] = 4.5
                    elif "링크" in key:
                        url_match = re.search(r'(https?://[^\s()]+)', val)
                        if url_match:
                            pension_data["metadata"]["링크"] = url_match.group(1).strip()
                        else:
                            pension_data["metadata"]["링크"] = val.strip()

        # 2. Kids Facilities
        elif "키즈 시설" in header or "키즈시설" in header:
            pension_data["kids_facilities"] = [l.strip("- ").strip() for l in section_content if l.startswith("-")]

        # 3. General Facilities / Room info
        elif "일반 시설" in header or "일반시설" in header or "객실 구성" in header or "객실구성" in header:
            facilities = [l.strip("- ").strip() for l in section_content if l.startswith("-")]
            pension_data["general_facilities"].extend(facilities)

        # 4. Pros
        elif "장점" in header:
            pension_data["pros"] = [l.strip("- ").strip() for l in section_content if l.startswith("-")]

        # 5. Cons
        elif "단점" in header:
            pension_data["cons"] = [l.strip("- ").strip() for l in section_content if l.startswith("-")]

        # 6. Memos
        elif "메모" in header:
            memo_lines = [l.strip("- ").strip() for l in section_content if not l.startswith("![")]
            pension_data["memo"] = " ".join(memo_lines)

    # Extract all obsidian image attachments ![[image_name.jpg]] from the entire file
    img_matches = re.findall(r'!\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', content)
    for img_name in img_matches:
        img_name = img_name.strip()
        # Find this image file in the vault
        found_path = find_image_file(img_name)
        if found_path:
            # Copy to F:\pension\assets\pension_images
            dest_path = os.path.join(assets_dir, img_name)
            try:
                shutil.copy2(found_path, dest_path)
                # Reference relative path for frontend
                web_path = f"assets/pension_images/{img_name}"
                if web_path not in pension_data["images"]:
                    pension_data["images"].append(web_path)
            except Exception as e:
                print(f"Error copying {img_name}: {e}")

    # Set cover image (default to first image, or placeholder if none)
    pension_data["cover_image"] = pension_data["images"][0] if pension_data["images"] else "assets/placeholder.jpg"

    return pension_data

def main():
    if not os.path.exists(notes_dir):
        print(f"Error: Notes directory {notes_dir} does not exist!")
        return

    all_pensions = []
    
    # Read each markdown file in the folder
    for filename in sorted(os.listdir(notes_dir)):
        if filename.endswith(".md"):
            file_path = os.path.join(notes_dir, filename)
            print(f"Processing note: {filename}...")
            try:
                data = parse_pension_note(file_path)
                all_pensions.append(data)
            except Exception as e:
                print(f"Failed to parse {filename}: {e}")

    # Create JS file containing the data
    js_content = f"// This file is auto-generated by build_dashboard.py. Do not edit directly.\n"
    js_content += f"const pensionsData = {json.dumps(all_pensions, ensure_ascii=False, indent=2)};\n"
    
    with open(output_js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print(f"\nSuccess! Standardized data for {len(all_pensions)} pensions written to {output_js_path}")
    print(f"All room images copied to {assets_dir} successfully!")

if __name__ == "__main__":
    main()
