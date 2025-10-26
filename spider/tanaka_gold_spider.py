import os
import re
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

# target url
URL = "https://gold.tanaka.co.jp/commodity/souba/index.php"

# wechat
APP_ID = "wx65afdf513aad7a56"
APP_SECRET = "89101d236fc04d0dab78df89fbdadcca"
TEMPLATE_ID: "J5rY-XMl65BjgG99ldVjv3qcatc-nQbkhvZFJYmJOU4"
USER_LIST = ["oSqB92P6yHW-StYAD8eXaIe9LgEo", "oSqB92NvA8uH0wMaaw-0cwv2TwNw"]
WECHAT_URL = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APP_ID}&secret={APP_SECRET}"

# telegram
CHAT_ID = "5799414614"
BOT_TOKEN = "8279886943:AAF2am55Vw5EMRKwt0jhb_ojP5wPQx3HTmY"
TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# CSV文件名
CSV_FILE = "tanaka_gold.csv"

# 当前时间
LOCAL_DATE = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# 定义一个函数(抓取今日金价)
def fetch_today_gold_price():
    try:
        # 使用 requests 库向上面的 URL 发送 HTTP 请求，获取网页内容(timeout: 设置超时时间为 10 秒，防止网页卡死。)
        # 执行后 res 是一个 Response 对象，包含网页的 HTML、状态码、headers 等信息
        res = requests.get(URL, timeout=10)
        # 强制把响应内容当成 UTF-8 编码解析
        res.encoding = "utf-8"
        # 用 BeautifulSoup 库解析 HTML 内容(网页的 HTML 字符串, html.parser: 指定使用 Python 内置的 HTML 解析器)
        # BeautifulSoup 会把 HTML 转成一个“可搜索的树状结构”，方便你用 select()、find() 等方法去提取元素。
        soup = BeautifulSoup(res.text, "html.parser")
        # print("soup", soup)

        # --- 获取日期时间 ---
        # 使用 CSS 选择器语法，从解析后的 HTML 中选择第一个符合条件的元素
        # 选中h3 tag
        h3_tag = soup.select_one("h3")

        # 提取 h3 中的 span 文本
        time_text = h3_tag.select_one("span").get_text(strip=True)
        # print("time", time_text)

        # --- 获取店头金的买取价格 ---
        table_tag = soup.select_one("table")
        # print("table_tag: ", table_tag)

        rows = table_tag.find_all("tr")

        data = []
        for row in rows:
            th = row.find("th")
            td = row.find("td")
            if th and td:
                # 提取并清理文字
                title = th.get_text(" ", strip=True)
                value = td.get_text(" ", strip=True)
                data.append({
                    "公表時間": time_text,
                    "项目": title,
                    "金额": value,
                    "当前时间": LOCAL_DATE
                })
        return data
    except Exception as e:
        print("抓取失败:", e)
        return []


def save_to_csv(data):
    if not data:
        return
    # 转成DataFrame
    df = pd.DataFrame(data)
    # 如果文件存在则追加，否则写入表头
    df.to_csv(CSV_FILE, mode='a', header=not os.path.exists(CSV_FILE), index=False, encoding="utf-8-sig")
    print(f"✅ {LOCAL_DATE} 数据已保存到 {CSV_FILE}")


def send_telegram_message(message):
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(TELEGRAM_URL, data=payload)
        print("telegram发送消息成功:", payload)
    except Exception as e:
        print("telegram发送消息失败:", e)


def send_message_to_wechat(data):
    try:
        res = requests.get(WECHAT_URL)
        access_token = res.json().get("access_token")
        url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={access_token}"

        for user in USER_LIST:
            payload = {
                "touser": user,
                "template_id": TEMPLATE_ID,
                "data": {
                    "date": {"value": data.get("date")},
                    "price": {"value": data.get("price")},
                    "change": {"value": data.get("change")},
                    "time": {"value": data.get("localTime")}
                }
            }
            res = requests.post(url, json=payload)
            print("wechat送信成功: ", res.json())
    except Exception as e:
        print("wechat送信失败: ", e)


def format_message(data_list):
    if not data_list:
        return "抓取失败或没有数据"

    lines = ["📊 田中贵金属 最新金价："]
    for row in data_list:
        # row = [抓取时间, 公表时间, 项目, 价格]
        lines.append(f"🕒 公表時間：{row.get('公表時間', '')}\n"
                     f"💰 {row.get('项目', '')}：{row.get('金额', '')}\n"
                     f"⏱ 抓取时间：{LOCAL_DATE}\n")
    return "\n".join(lines)


def get_last_record():
    try:
        """用 pandas 读取 CSV 的最后一行"""
        if not os.path.exists(CSV_FILE):
            return None

        cols = ['公表時間', '項目', '金额', '执行时间']
        df = pd.read_csv(CSV_FILE, encoding="utf-8-sig", names=cols, header=0)
        if df.empty:
            return None

        # 表格对象的最后一行，并把结果转为字典
        print("获取CSV最后一行数据成功: ", df.iloc[-1].to_dict())
        return df.iloc[-1].to_dict()
    except Exception as e:
        print("获取CSV最后一行数据失败: ", e)


def format_wechat_message(data_list):
    data = data_list[1]
    price = ""
    change = ""
    match = re.match(r"([\d,]+)\s*円\s*\(([-+]\d+)\s*円\)", data.get("金额"))
    if match:
        price = match.group(1)
        change = match.group(2)

    send_data = {
        "date": data.get("公表時間"),
        "price": price,
        "change": change,
        "localTime": LOCAL_DATE
    }
    return send_data


def main():
    try:
        print("程序执行start・・・")
        cnt = 0
        max_cnt = 3
        while cnt < max_cnt:
            data_list = fetch_today_gold_price()

            # 数据有效性判断
            new_data = data_list[0]
            print("new_data", new_data)
            if not new_data["公表時間"] or not new_data["项目"] or not new_data["金额"]:
                print("⚠️ 获取失败，网页结构可能变动。")
                cnt += 1
                return

            # 获取文件最后的数据
            last_record = get_last_record()
            print("last_record: ", last_record)

            if last_record and last_record["公表時間"] == new_data["公表時間"]:
                print("⏸ 没有新数据，不推送。")
                if cnt < max_cnt:
                    time.sleep(5 * 60)  # 等 5 分钟再检测
            else:
                print("✅ 检测到新数据：", data_list)
                save_to_csv(data_list)
                message_text = format_message(data_list)  # 转成字符串
                send_telegram_message(message_text)
                send_data = format_wechat_message(data_list)
                send_message_to_wechat(send_data)
                break
    except Exception as e:
        print("⚠️ 用户中断程序，正在安全退出...", e)
    finally:
        print("程序执行end・・・")


if __name__ == "__main__":
    main()
