#!/usr/bin/env python3
import argparse
import json
import re
import sys
import requests
import time

def clean_results(results):
    cleaned = set()
    for r in results:
        if not r: continue
        for line in re.split(r"[\n,]", str(r)):
            line = line.strip().replace("*.", "")
            if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}", line):
                continue
            if line:
                cleaned.add(line.lower())
    return sorted(cleaned)

def filter_by_root(domains, root):
    root = root.lower()
    return [d for d in domains if d == root or d.endswith("." + root)]

def make_request(url, max_retries=10):
    # محاولات أكتر مع وقت انتظار أطول لضمان تخطي الـ 502 والـ Rate Limit
    for i in range(max_retries):
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200 and r.text.startswith("["):
                return json.loads(r.text)
            
            # لو السيرفر مضغوط، استنى وقت بيزيد مع كل محاولة فاشلة
            wait_time = (i + 1) * 10 
            time.sleep(wait_time)
            
        except Exception:
            time.sleep(10)
            continue
    return None

def search_domain(domain):
    encoded = domain.replace(".", "%25.")
    url = f"https://crt.sh/?q=%25.{encoded}&output=json"
    data = make_request(url)
    
    if data:
        raw = []
        for entry in data:
            raw.append(entry.get("common_name"))
            raw.append(entry.get("name_value"))
        
        results = filter_by_root(clean_results(raw), domain)
        for r in results:
            print(r) # دي الحاجة الوحيدة اللي هتظهر في الـ Terminal أو الملف

def search_org(org):
    url = f"https://crt.sh/?q={org}&output=json"
    data = make_request(url)
    
    if data:
        raw = [entry.get("common_name") for entry in data]
        results = clean_results(raw)
        for r in results:
            print(r)

def main():
    parser = argparse.ArgumentParser(description="Silent crt.sh enumerator")
    parser.add_argument("-d", "--domain", help="Domain to search")
    parser.add_argument("-o", "--org", help="Org to search")
    args = parser.parse_args()

    if args.domain:
        search_domain(args.domain)
    elif args.org:
        search_org(args.org)

if __name__ == "__main__":
    main()