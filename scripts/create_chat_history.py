import os
import yaml
import random
import requests
from datetime import date
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# ===== 基础路径 =====
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
CONFIG_PATH = BASE_DIR / "config" / "users.yml"

# ===== 读取配置 =====
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

users = config["users"]

# ===== 从环境变量读取 BASE_URL =====
base_url = os.getenv("BASE_URL")
if not base_url:
    raise RuntimeError("BASE_URL environment variable not set")

today = date.today().isoformat()


def call_api(user):
    token = user.get("token")
    if not token:
        raise RuntimeError(f"token not set for user {user['name']}")

    rounds = random.randint(1, 3)

    url = f"{base_url}/api/v1/digital_lifes/{user['digital_life_id']}/chat_history/generate"

    try:
        resp = requests.post(
            url,
            headers={"Authorization": f"Bearer {token}"},
            json={
                "date": today,
                "rounds": rounds,
                "device_id": user["device_id"]
            },
            timeout=60
        )

        return {
            "user": user["name"],
            "status": resp.status_code,
            "response": resp.text
        }

    except Exception as e:
        return {
            "user": user["name"],
            "status": "ERROR",
            "response": str(e)
        }


# ===== 并发执行 =====
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(call_api, user) for user in users[:3]]

    for future in as_completed(futures):
        result = future.result()
        print("========== CALL RESULT ==========")
        print("User    :", result["user"])
        print("Status  :", result["status"])
        print("Response:", result["response"])
