import json
import logging
import os
from datetime import datetime, timedelta, timezone, time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv, find_dotenv

import telegram_client as tele_cli
import wechat_client as wechat_cli

load_dotenv(find_dotenv(), True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def price_change_fetch():
    try:
        base_url = os.environ["BASE_URL"]
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
        logging.info("抓取数据失败: %s", e)
        return []


def write_json(data):
    file_path = os.environ["JSON_PATH"]
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def read_json_last_record():
    file_path = "base_price.json"
    with open(file_path, "r", encoding="UTF-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if lines:
        last_record = json.loads(lines[-1])
        logging.info(f"最后一条记录：{last_record}")
        return last_record
    else:
        logging.info("文件为空或没有有效记录")
        return None


def main():
    logging.info("实时金价查询开始・・・")
    rst = price_change_fetch()
    logging.info(f"rst: {rst}")

    dt_time = datetime.strptime(rst["dt_time"], "%Y-%m-%d %H:%M")
    if dt_time.time() == time(11, 30) and dt_time.date() == datetime.now().date():
        data = {
            "date": rst["dt_time"],
            "price": rst["rate"]
        }
        write_json(data)

    last_record = read_json_last_record()
    if last_record and last_record["price"] is not None:
        base_price = float(last_record["price"].replace(",", ""))
        now_price = float(rst["rate"].replace(",", ""))
        try:
            if abs(now_price - base_price) > 200:
                wechat_cli.send_message(rst)
        except ValueError:
            logging.info("价格数据不是数字，跳过比较")

    tele_cli.send_message(rst)

    logging.info("实时金价查询结束・・・")


if __name__ == "__main__":
    main()
