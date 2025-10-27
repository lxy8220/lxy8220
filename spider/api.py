import os

import requests
from bs4 import BeautifulSoup


def fetch_soup(env_key: str, timeout: int = 10) -> BeautifulSoup | None:
    try:
        url = os.getenv(env_key)
        res = requests.get(url, timeout=timeout)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")

        return soup
    except Exception as e:
        print(f"请求出错: {e}")
        return None
