import yaml
import random
import requests
from datetime import date
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "users.yml"

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

base_url = config["base_url"]
today = date.today().isoformat()
users = config["users"]

def call_api(user):
    rounds = random.randint(1, 9)
    url = f"{base_url}/api/v1/digital_lifes/{user['digital_life_id']}/chat_history/generate"

    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {user['token']}"},
        json={
            "date": today,
            "rounds": rounds,
            "device_id": user["device_id"]
        },
        timeout=60
    )

    return {
        "user": user.get("name"),
        "status": resp.status_code,
        "response": resp.text
    }

# ⭐ 核心：并发 3 次
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(call_api, user) for user in users[:3]]

    for future in as_completed(futures):
        result = future.result()
        print("========== CALL RESULT ==========")
        print("User    :", result["user"])
        print("Status  :", result["status"])
        print("Response:", result["response"])
