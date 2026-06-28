import json
import logging
import os
import re

import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), True)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


COMMON_HEADER = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://epark.jp/",
    "Origin": "https://epark.jp",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json"
}


def get_shop_ntc_fetch():
    try:
        base_url = "https://api.faspa.epark.jp/v2/api/shop/justpass/receipt/confirm/entry-no?media_shop_id=6633&entry_no=111"

        res = requests.get(base_url, headers=COMMON_HEADER)
        res.encoding = "utf-8"
        res.raise_for_status()
        res_data = res.json()

        return res_data
    except Exception as e:
        logging.info("抓取数据失败: %s", e)
        return []


def main():
    logging.info("查询开始・・・")

    shop_rst = get_shop_ntc_fetch()
    logging.info(f"shop_rst: {shop_rst}")
    re_str = shop_rst['entryInfo'][0]['waitCountText']
    num = int(re.search(r"\d+", re_str).group())
    if shop_rst['entryInfo'][0]['guideStatus'] == 1 and num == 3:
        send_message(shop_rst['entryInfo'][0]['waitCountText'])


def send_message(str):
    try:
        load_dotenv()
        app_id = os.getenv("APP_ID")
        app_secret = os.getenv("APP_SECRET")
        user_list = json.loads(os.getenv("USER_LIST"))
        template_id = os.getenv("UR_TEMPLATE_ID")

        get_access_token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&" \
                               f"appid={app_id}&secret={app_secret}"

        res = requests.get(get_access_token_url, timeout=10)
        access_token = res.json().get("access_token")
        if access_token is None:
            print("access_token not found in response")
            return
        send_msg_url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?" \
                       f"access_token={access_token}"

        data = {
            "msg": {"value": "🚨🔥 ご案内まで後" + str}
        }
        logging.info(f"shop_rst: {data}")

        for user in user_list:
            payload = {
                "touser": user,
                "template_id": template_id,
                "data": data
            }
            res = requests.post(send_msg_url, json=payload)
            if res.json()["errcode"] == 0:
                print("wechat送信成功: ", res.json())
            else:
                print("wechat送信失敗: ", res.json())

    except Exception as e:
        print("wechat送信失败: ", e)


if __name__ == "__main__":
    main()


