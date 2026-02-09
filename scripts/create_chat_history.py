import yaml
import random
import requests
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "users.yml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

base_url = config["base_url"]
today = date.today().isoformat()


for user in config["users"]:
    rounds = random.randint(1, 9)

    url = f"{base_url}/api/v1/digital_lifes/{user['digital_life_id']}/chat_history/generate"
    payload = {
        "date": today,
        "rounds": rounds,
        "device_id": user["device_id"]
    }

    try:
        resp = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {user['token']}"
            },
            json=payload,
            timeout=60
        )

        print("========== Generate Test Data ==========")
        print(f"User       : {user.get('name')}")
        print(f"Device ID  : {user['device_id']}")
        print(f"Rounds     : {rounds}")
        print(f"Status     : {resp.status_code}")

        try:
            print("Response   :", resp.json())
        except ValueError:
            print("Response   :", resp.text)

    except Exception as e:
        print("========== Generate Test Data FAILED ==========")
        print(f"User       : {user.get('name')}")
        print(f"Device ID  : {user['device_id']}")
        print("Error      :", str(e))
