from pprint import pprint
from requests import get
from math import floor
from datetime import datetime
from time import time

def download_file (filename, url):
    with open(filename, "wb") as f:
        response = get(url)
        f.write(response.content)

download_file("blacklisted_websites.txt", "https://github.com/Charcoal-SE/SmokeDetector/raw/master/blacklisted_websites.txt")

with open("blacklisted_websites.txt", "r") as f:
    blacklisted_websites = []
    for line in f:
        if len(line.strip()) > 0:
            blacklisted_websites.append(str(line.strip()))

def search_body (keyword):
    return get("https://metasmoke.erwaysoftware.com/search.json?body={}&body_is_regex=1".format(keyword))

for website in blacklisted_websites[:5]:
    posts = search_body(website).json()

    tps, fps, naa = 0, 0, 0
    last_tp = "N/A"

    for post in posts:
        if post['is_tp']:
            tps += 1
            last_tp = post['created_at']
        elif post['is_fp']:
            fps += 1
        elif post['is_naa']:
            naa += 1

    try:
        accuracy = floor(tps / (tps + fps + naa) * 100)
    except ZeroDivisionError:
        accuracy = 0
    last_tp_text = last_tp
    try:
        last_tp = datetime.strptime(last_tp, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
    except ValueError:
        last_tp = 0.0

    reasons = []

    if accuracy <= 50:
        reasons.append("Not accurate enough")

    if time() - last_tp > 15768000: # > 6 months ago
        reasons.append("Last tp was > 6 months ago")

    print(website, "({} tps, {} fps, {} naa, {}% accuracy, last tp {})".format(tps, fps, naa, accuracy, last_tp_text))
    if len(reasons) > 0:
        print("Removal reason(s): {}\n".format(", ".join(reasons)))
