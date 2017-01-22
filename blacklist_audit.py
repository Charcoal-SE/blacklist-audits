from pprint import pprint
from requests import get
from math import floor
from datetime import datetime
from time import time

def download_file (filename, url):
    with open(filename, "wb") as f:
        response = get(url)
        f.write(response.content)


def search_body (keyword):
    print("https://metasmoke.erwaysoftware.com/search.json?body={}&body_is_regex=1".format(keyword))
    return get("https://metasmoke.erwaysoftware.com/search.json?body={}&body_is_regex=1".format(keyword))


def search_username (keyword):
    return get("https://metasmoke.erwaysoftware.com/search?username_is_regex=1&username={}".format(keyword))


def audit_blacklist (filename, search_type):
    """Audit the blacklist specified for usefulness and validity

    :param file_name: File name of the blacklist
    :param search_type: Field of posts to be searched (body or username)
    """
    with open(filename, "r") as f:
        blacklist = []
        for line in f:
            if len(line.strip()) > 0:
                blacklist.append(str(line.strip()))

    for item in blacklist[:5]: # For testing purposes only
        # Search body/username for blacklisted item
        if search_type == "body":
            posts = search_body(item).json()
        elif search_type == "username":
            posts = search_username(item).json()
        else:
            return "Invalid search type"

        tps, fps, naa = 0, 0, 0
        last_tp = "N/A"

        # Find TP/FP/NAA breakdown
        for post in posts:
            if post['is_tp']:
                tps += 1
                last_tp = post['created_at']
            elif post['is_fp']:
                fps += 1
            elif post['is_naa']:
                naa += 1

        # Determine accuracy
        try:
            accuracy = floor(tps / (tps + fps + naa) * 100)
        except ZeroDivisionError:
            accuracy = 0

        # Find the number of seconds since Epoch the last TP was found
        last_tp_text = last_tp
        try:
            last_tp = datetime.strptime(last_tp, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
        except ValueError:
            last_tp = 0.0

        reasons = []

        # Require at least 50% accuracy
        if accuracy <= 50:
            reasons.append("Not accurate enough")

        # Last TP must have been no longer than 1 year ago
        if time() - last_tp > (365 * 24 * 60 * 60):
            reasons.append("Last TP was > 1 year ago")

        # Print summary
        print(item, "({} tps, {} fps, {} naa, {}% accuracy, last tp {})".format(tps, fps, naa, accuracy, last_tp_text))
        if len(reasons) > 0:
            print("Removal reason(s): {}\n".format(", ".join(reasons)))

def main ():
    download_file("blacklisted_websites.txt", "https://github.com/Charcoal-SE/SmokeDetector/raw/master/blacklisted_websites.txt")
    audit_blacklist("blacklisted_websites.txt", "body")

    #download_file("bad_keywords.txt", "https://github.com/Charcoal-SE/SmokeDetector/raw/master/bad_keywords.txt")
    #audit_blacklist("bad_keywords.txt", "body")

if __name__ == "__main__":
    main()
