import os
import subprocess

assets_dir = r"F:\pension\assets\pension_images"

# List of old file prefixes we want to remove
old_prefixes = ["room_328_", "room_337_", "room_709_", "room_740_", "room_789_", "room_828_"]

if not os.path.exists(assets_dir):
    print("Assets folder not found.")
    exit(1)

deleted_count = 0
for filename in os.listdir(assets_dir):
    # Check if the filename starts with any of our old prefixes AND does not contain "_room_"
    # For example, "room_328_0.jpg" is old, but "room_328_room_1.jpg" is new and ordered!
    is_old = False
    for pref in old_prefixes:
        if filename.startswith(pref) and "_room_" not in filename:
            is_old = True
            break
            
    if is_old:
        file_path = os.path.join(assets_dir, filename)
        try:
            # Delete file
            os.remove(file_path)
            print(f"Deleted local file: {filename}")
            
            # Run git rm if tracked
            subprocess.run(["git", "rm", "-f", file_path], Cwd=r"F:\pension", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            deleted_count += 1
        except Exception as e:
            print(f"Error deleting {filename}: {e}")
            
print(f"Cleanup finished! Removed {deleted_count} old unordered assets.")
