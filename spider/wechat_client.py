import json
import os

import requests
from dotenv import load_dotenv


def send_message(data):
    try:
        load_dotenv()
        app_id = os.getenv("APP_ID")
        app_secret = os.getenv("APP_SECRET")
        user_list = json.loads(os.getenv("USER_LIST"))
        template_id = os.getenv("TEMPLATE_ID")
        get_access_token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&" \
                               f"appid={app_id}&secret={app_secret}"

        res = requests.get(get_access_token_url, timeout=10)
        access_token = res.json().get("access_token")
        if access_token is None:
            print("access_token not found in response")
            return
        send_msg_url = f"https://api.weixin.qq.com/cgi-bin/message/template/send?" \
                       f"access_token={access_token}"

        for user in user_list:
            payload = {
                "touser": user,
                "template_id": template_id,
                "data": {
                    "date": {"value": data["dt_time"]},
                    "price": {"value": data["rate"]},
                    "change": {"value": data["change"]},
                    "time": {"value": data["local_dt_time"]}
                }
            }
            res = requests.post(send_msg_url, json=payload)
            if res.json()["errcode"] == 0:
                print("wechat送信成功: ", res.json())
            else:
                print("wechat送信失敗: ", res.json())

    except Exception as e:
        print("wechat送信失败: ", e)
