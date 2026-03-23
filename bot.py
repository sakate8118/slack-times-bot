import os
import json
from datetime import datetime, timedelta, timezone
from slack_sdk import WebClient

SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
client = WebClient(token=SLACK_TOKEN)

CHANNEL_ATTENDANCE = "CXXXXXXXX"  # 勤怠
CHANNEL_TIMES = "CXXXXXXXX"       # times

JST = timezone(timedelta(hours=9))
STATE_FILE = "notified_users.json"


# 状態読み込み
def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


# 状態保存
def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


# 今日の日付キー
def today_key():
    now = datetime.now(JST)
    return now.strftime("%Y-%m-%d")


# インターン生取得
def get_intern_users():
    users = client.users_list()["members"]
    return [
        u for u in users
        if not u.get("deleted")
        and u.get("profile", {}).get("title") == "インターン生"
    ]


# 今日の投稿取得
def get_today_messages(channel_id):
    now = datetime.now(JST)
    start = datetime(now.year, now.month, now.day, tzinfo=JST)

    res = client.conversations_history(
        channel=channel_id,
        oldest=start.timestamp()
    )
    return res["messages"]


# 投稿数カウント
def count_user_messages(messages, user_id):
    return sum(1 for m in messages if m.get("user") == user_id)


# 最終投稿時間
def get_last_post_time(channel_id, user_id):
    res = client.conversations_history(channel=channel_id, limit=100)
    for m in res["messages"]:
        if m.get("user") == user_id:
            return datetime.fromtimestamp(float(m["ts"]), JST)
    return None


# DM送信
def send_dm(user_id, text):
    # DM用チャンネル作成
    dm = client.conversations_open(users=user_id)
    channel_id = dm["channel"]["id"]

    client.chat_postMessage(
        channel=channel_id,
        text=text
    )


def main():
    state = load_state()
    today = today_key()

    if today not in state:
        state = {today: []}  # 日付変わったらリセット

    attendance_msgs = get_today_messages(CHANNEL_ATTENDANCE)
    interns = get_intern_users()

    now = datetime.now(JST)

    for user in interns:
        user_id = user["id"]

        # ① 勤怠1回のみ
        if count_user_messages(attendance_msgs, user_id) != 1:
            continue

        # ② 最終投稿
        last_post = get_last_post_time(CHANNEL_TIMES, user_id)
        if not last_post:
            continue

        # ③ 30分経過
        if now - last_post < timedelta(minutes=30):
            continue

        # ④ すでに通知済みならスキップ
        if user_id in state[today]:
            continue

        # ⑤ DM通知
        send_dm(user_id, "30分以上 #times-intern の更新がありません。投稿をお願いします！")

        # 記録
        state[today].append(user_id)

    save_state(state)


if __name__ == "__main__":
    main()