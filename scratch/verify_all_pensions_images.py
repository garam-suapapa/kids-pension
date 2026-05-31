import os
import re

vault_dir = r"F:\pension\Obsidian Vault"
notes_dir = os.path.join(vault_dir, "펜션정리")

if not os.path.exists(notes_dir):
    print("Notes directory not found.")
    exit(1)

notes = sorted([f for f in os.listdir(notes_dir) if f.endswith(".md")])
print(f"Verifying {len(notes)} pension notes for image attachments:")

missing_any = []

for idx, filename in enumerate(notes, 1):
    file_path = os.path.join(notes_dir, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    img_matches = re.findall(r'!\[\[([^\]|]+)(?:\|[^\]]*)?\]\]', content)
    print(f"[{idx}] {filename} -> Found {len(img_matches)} linked images")
    
    if not img_matches:
        missing_any.append(filename)
        
if missing_any:
    print("\n--- PENSIONS MISSING LINKED IMAGES ---")
    for f in missing_any:
        print(f"  - {f}")
else:
    print("\nAll pensions have image attachments linked in their notes!")
