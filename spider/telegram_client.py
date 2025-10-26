import os

import requests
from dotenv import load_dotenv


def send_message(message):
    load_dotenv()
    chat_id = os.getenv("CHAT_ID")
    access_token = os.getenv("ACCESS_TELEGRAM_TOKEN")
    telegram_url = f"https://api.telegram.org/bot{access_token}/sendMessage"

    try:
        fmt_msg = format_message(message)
        payload = {"chat_id": chat_id, "text": fmt_msg, "parse_mode": "HTML"}
        requests.post(telegram_url, data=payload)
        print("telegram发送消息成功:", payload)
    except Exception as e:
        print("telegram发送消息失败:", e)


def format_message(data):
    if not data:
        return "telegram传输数据为空或没有数据"
    print(data)
    lines = (["📊 <b color='#ff0000'>今日实时金价:</b> ",
              f"🕒 公表時間: {data['dt_time']}\n"
              f"💰 金额: {data['rate']}\n"
              f"{change_emoji(data['change'])} 变动: {data['change']}\n"
              f"⏱ 抓取时间：{data['local_dt_time']}\n"])
    return "\n".join(lines)


def change_emoji(change):
    float_change = float(change)
    if float_change > 0:
        return "🟢"
    elif float_change < 0:
        return "🔴"
    else:
        return "➖"
