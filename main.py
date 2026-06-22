import os
import requests
import time

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHANNEL = os.getenv("TELEGRAM_CHANNEL")

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USERNAME = os.getenv("TWITCH_USERNAME")

message_id = None
was_live = False


def get_token():
    r = requests.post(
        "https://id.twitch.tv/oauth2/token",
        params={
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials",
        },
    )
    return r.json()["access_token"]


def get_stream(token):
    r = requests.get(
        f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}",
        headers={
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {token}",
        },
    )

    data = r.json().get("data", [])

    if len(data) > 0:
        return data[0]

    return None


def send_message(title, game):
    text = (
        f"🔴 Gelle_x вышла в эфир!\n\n"
        f"🎮 {game}\n"
        f"📝 {title}"
    )

    r = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHANNEL,
            "text": text,
            "reply_markup": {
                "inline_keyboard": [[
                    {
                        "text": "🎥 Смотреть стрим",
                        "url": f"https://twitch.tv/{TWITCH_USERNAME}"
                    }
                ]]
            }
        },
    )

    result = r.json()

    print("Telegram response:", result)

    return result["result"]["message_id"]


def delete_message(msg_id):
    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteMessage",
        json={
            "chat_id": TELEGRAM_CHANNEL,
            "message_id": msg_id,
        },
    )


token = get_token()

print("Bot started")
print("Watching:", TWITCH_USERNAME)

while True:
    try:
        stream = get_stream(token)

        if stream and not was_live:
            print("Stream started")

            message_id = send_message(
                stream["title"],
                stream["game_name"]
            )

            was_live = True

        elif not stream and was_live:
            print("Stream ended")

            delete_message(message_id)

            was_live = False
            message_id = None

    except Exception as e:
        print("ERROR:", e)

    time.sleep(60)
