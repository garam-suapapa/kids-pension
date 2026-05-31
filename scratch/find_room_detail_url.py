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
        
    print("Searching for JS functions related to room loading:")
    # Look for functions like function view, function show, $.ajax, etc.
    funcs = re.findall(r'function\s+\w+\([^)]*\)\s*\{[^}]*\}', html)
    print("Found standard functions:", len(funcs))
    
    # Let's search for keywords in script tags
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    print("Found script blocks:", len(scripts))
    
    # Print lines in script tags that contain "ajax" or "url" or "room" or "id" or "view"
    for i, script in enumerate(scripts):
        lines = script.split('\n')
        matching_lines = []
        for line in lines:
            if any(k in line for k in ['ajax', 'post', 'get', 'html', '/room/', 'detail', 'view', 'location.href']):
                matching_lines.append(line.strip())
        if matching_lines:
            print(f"\nMatching lines in Script Block {i}:")
            for ml in matching_lines[:15]:
                print("  ", ml[:120])
                
except Exception as e:
    print("Error:", e)
