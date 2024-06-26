#!/usr/bin/env python3

import requests
import time
import sys
import os
import subprocess
import logging
import json
from io import TextIOWrapper

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from fake_headers import Headers

WAIT = 10
URL = f"https://www.dhl.com/es-es/home/tracking/tracking-express.html?submit=1&tracking-id="
UPDATE_CLASS = "c-tracking-result--status-copy-date"
TITLE_CLASS = "c-tracking-result--status-copy-message"
RESULT_FILE = "/tmp/deliver_result.txt"
LOG_FILE = "/tmp/deliver.log"

logging.basicConfig(
    format="%(asctime)s %(message)s",
    filename=LOG_FILE,
    encoding="utf-8",
    level=logging.WARNING,
)

header = Headers(browser="chrome", os="lin", headers=False)
customUserAgent = header.generate()["User-Agent"]

# browser options
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument(f"user-agent={customUserAgent}")

# request page, waiting 10 seconds
browser = webdriver.Chrome(options=chrome_options)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_last_update() -> dict:
    browser.get(URL)
    wait = WebDriverWait(browser, WAIT)

    selector = f"div.{UPDATE_CLASS}"

    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
    except:
        logging.warning(f"Could not find CSS_SELECTOR -> {selector}")
        exit(0)

    # parse response
    html = browser.page_source
    soup = BeautifulSoup(html, "html.parser")
    element = f'{str(soup.find("div", class_=UPDATE_CLASS).text).strip()}\n'
    title = (
        f'{str(soup.find("h2", class_=TITLE_CLASS).text).partition(",")[0].strip()}\n'
    )

    return {"data": element, "title": title}


def is_new_update(data: str) -> bool:
    if not os.path.exists(RESULT_FILE):
        return True

    with open(RESULT_FILE, "r") as file:
        line = file.readline()
        logging.warning(line)
        if line == data:
            return False

    return True


def write_in_file(data: str) -> None:
    with open(RESULT_FILE, "w") as file:
        file.write(data)


def send_notification(data: dict) -> None:
    subprocess.call(["dunstify", data["title"], data["data"], "-u", "critical"])


def send_phone_notification(data: dict) -> None:
    msg = {"type": "note", "title": data["title"], "body": data["data"]}

    resp = requests.post(
        "https://api.pushbullet.com/v2/pushes",
        data=json.dumps(msg),
        headers={
            "Authorization": "Bearer " + sys.argv[2],
            "Content-Type": "application/json",
        },
    )

    if resp.status_code != 200:
        logging.warning("Exception while sending phone notification")
        raise Exception("Error", resp.status_code)
    else:
        logging.warning("Message sent")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        eprint(f"Usage: {sys.argv[0]} <id> <token>")
        eprint(f"\t<id>: your dhl package id")
        eprint(f"\t<token>: your PushBullet token")
        exit(0)

    URL = f"{URL}{sys.argv[1]}"

    data = get_last_update()

    if is_new_update(data["data"]):
        write_in_file(data["data"])
        send_notification(data)
        if len(sys.argv) == 3:
            send_phone_notification(data)

    # quit
    browser.quit()
