import os
from datetime import datetime, timedelta, timezone

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import telegram_client as tele_cli
import wechat_client as wechat_cli


def price_change_fetch():
    try:
        load_dotenv()
        base_url = os.getenv("BASE_URL")
        res = requests.get(base_url, timeout=10)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")

        tag = soup.select_one("table#dtDGrid")
        rows = tag.select_one("tr.DataRow")

        date = rows.select_one("td.Date")
        span = date.select_one("span#utc_0")
        dt_str = span["dt"]
        # 转换为日本时间
        utc_time = datetime.strptime(dt_str, "%Y-%m-%d-%H-%M").replace(tzinfo=timezone.utc)
        jst_time = utc_time.astimezone(timezone(timedelta(hours=9)))
        dt_time = jst_time.strftime("%Y-%m-%d %H:%M")

        rate = rows.select_one("td.rate").get_text(strip=True)
        change = rows.select_one("td.rate.Change").find("span").get_text(strip=True)

        data = {
            "dt_time": dt_time,
            "rate": rate,
            "change": change,
            "local_dt_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        return data
    except Exception as e:
        print("抓取数据失败", e)
        return []


def main():
    print("实时金价查询开始・・・")
    rst = price_change_fetch()
    print("rst: ", rst)
    tele_cli.send_message(rst)
    wechat_cli.send_message(rst)
    print("实时金价查询结束・・・")


if __name__ == "__main__":
    main()
