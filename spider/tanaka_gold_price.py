import logging
import os
import time
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from api import fetch_soup
import telegram_client as tele_cli
import wechat_client as wechat_cli

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


# 定义一个函数(抓取今日金价)
def fetch_today_gold_price():
    try:
        soup = fetch_soup("TANAKA_BASE_URL")

        time_text = soup.select_one("h3 span").get_text(strip=True) if soup.select_one("h3 span") else ""
        rows = soup.select_one("table").find_all("tr") if soup.select_one("table") else []

        data_list = []
        for row in rows:
            title = row.find("th").get_text(" ", strip=True) if row.find("th") else ""
            value = row.find("td").get_text(" ", strip=True) if row.find("td") else ""

            if title and value:
                data_list.append({
                    "dt_time": time_text,
                    "title": title,
                    "rate": value,
                    "local_dt_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })

        return data_list
    except Exception as e:
        logging.info("抓取失败: %s", e)
        return {}


def get_last_record():
    logging.info("读取CSV文件开始・・・")
    file_path = get_file_path()
    try:
        df = pd.read_csv(file_path, encoding="utf-8-sig")
        if df.empty:
            logging.info("CSV 文件为空")
            return None

        # 表格对象的最后一行，并把结果转为字典
        return df.iloc[-1].to_dict()
    except Exception as e:
        logging.info("获取CSV最后一行数据失败: %s", e)
        return None


def get_file_path():
    file_path = os.getenv("CSV_FILE")
    if not file_path or not os.path.exists(file_path):
        logging.info("CSV 文件不存在或路径未设置")
        return None
    return file_path


def save_to_csv(data):
    if not data:
        return
    df = pd.DataFrame(data)
    file_path = get_file_path()

    df.to_csv(file_path, mode='a', header=not os.path.exists(file_path), index=False, encoding="utf-8-sig")


def main():
    try:
        logging.info("程序执行开始・・・")
        data_list = fetch_today_gold_price()
        if not data_list:
            logging.info("main()_没有抓取到数据")
            return None

        cnt = 0
        max_cnt = int(os.getenv("MAX_CNT", "3"))
        new_data = data_list[0]
        while cnt < max_cnt:
            last_record = get_last_record()
            if not last_record:
                logging.info("获取CSV文件数据失败")
                return None
            if last_record["公表時間"] == new_data["dt_time"]:
                logging.info(f"⏸ 没有新数据，等待 3 分钟后再检测 (第 {cnt}/{max_cnt} 次)")
                cnt += 1
                time.sleep(3 * 60)  # 等 3 分钟再检测
            else:
                logging.info("✅ 检测到新数据：%s", data_list)
                save_to_csv(data_list)
                tele_cli.send_message(data_list)
                wechat_cli.send_message(data_list)
                break
        else:
            logging.info("🔁 已检测 3 次，没有发现新数据，程序结束。")
    except KeyboardInterrupt:
        logging.info("⚠️ 用户中断程序，正在安全退出...")
    except Exception as e:
        logging.info("❌ 程序异常退出:", e)
    finally:
        logging.info("程序执行结束・・・")


if __name__ == "__main__":
    main()
