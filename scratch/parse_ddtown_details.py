import urllib.request
import re
import ssl

url = "https://www.ddtown.co.kr/room"
ctx = ssl.create_default_context()
ctx.set_ciphers('DEFAULT@SECLEVEL=1')
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8', errors='ignore')
    
    # We want to extract the full object for IDs 105, 110, and 200.
    # The objects are structured like:
    # {
    #     id:'105',
    #     ...
    # }
    
    ids_to_find = ['105', '110', '200']
    
    for room_id in ids_to_find:
        print(f"\n================ ID: {room_id} ================")
        # Find start of object: id:'room_id'
        # We search for the pattern id:'room_id' or id:"room_id"
        pattern = rf"id\s*:\s*['\"]{room_id}['\"]"
        match = re.search(pattern, html)
        if match:
            start_pos = match.start()
            # Find the closing brace of the object. We can scan forward for '}'
            # Since content is inside, let's grab the next 1000 characters to cover the whole entry.
            end_pos = min(len(html), start_pos + 1500)
            chunk = html[start_pos:end_pos]
            print(chunk)
        else:
            print(f"Not found in HTML!")
            
except Exception as e:
    print("Error:", e)
