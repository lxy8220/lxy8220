import json
import logging
import os
from datetime import datetime

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
    "Referer": "https://www.ur-net.go.jp/",
    "Origin": "https://www.ur-net.go.jp",
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}


COMMON_DATA = {
    "rent_low": "",
    "rent_high": "",
    "walk": "",
    "floorspace_low": "",
    "floorspace_high": "",
    "years": "",
    "mode": "eki",
    # "eki": "1742",
    "eki": "1896", # 亀戸
    "line": "4500",
    # "line_station": "4500_1742",
    "line_station": "4500_1896",  # 亀戸
    "block": "kanto",
    "tdfk": "",
    "rireki_tdfk": "13",
    "orderByField": "1",
    "pageSize": "10",
    "pageIndex": "0",
    "shisya": "",
    "danchi": "",
    "shikibetu": "",
    "pageIndexRoom": "0",
    "sp": ""
}


def post_ur_address_fetch():
    try:
        base_url = os.environ["UR_ADDRESS_BASE_URL"]

        res = requests.post(base_url, headers=COMMON_HEADER, data=COMMON_DATA)
        res.encoding = "utf-8"
        res_data = res.json()

        return res_data
    except Exception as e:
        logging.info("抓取数据失败: %s", e)
        return []


def post_ur_room_fetch():
    try:
        base_url = os.environ["UR_ROOM_BASE_URL"]

        res = requests.post(base_url, headers=COMMON_HEADER, data=COMMON_DATA)
        res.encoding = "utf-8"
        res_data = res.json()

        return res_data
    except Exception as e:
        logging.info("抓取数据失败: %s", e)
        return []


def main():
    logging.info("查询开始・・・")

    target_str = "江東区亀戸2-6"

    room_rst = post_ur_room_fetch()
    # logging.info(f"room_rst: {room_rst}")

    if room_rst:
        logging.info("★★★快上号，有新房了★★★")
        adr_rst = post_ur_address_fetch()
        # logging.info(f"adr_rst: {adr_rst}")
        if target_str in adr_rst[0].get("place", ""):
            send_message(room_rst, adr_rst)
            logging.info("★★★快上号，有新房了★★★")
        else:
            logging.info(f"place: {adr_rst[0].get('place')}")
            logging.info("残念ながら，亀戸２丁目の団地ではない・・・・")
    else:
        logging.info("◆◆◆房间数为空◆◆◆")
        return None


def send_message(room_info, ads_info):
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
            "msg": {"value": "🚨🔥 新房上线！手慢无！！"},
            "address": {"value": ads_info[0].get("place")},
            "roomInfo": {"value": room_info[0].get("roomNmMain") + "" + room_info[0].get("roomNmSub")},
            "time": {"value": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        }

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


