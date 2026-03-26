import os
import re
import yaml
import requests
from pathlib import Path
from dotenv import load_dotenv

# ===== 基础路径 =====
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
CONFIG_PATH = BASE_DIR / "config" / "users.yml"

# ===== 读取配置 =====
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    raw_content = f.read()

config = yaml.safe_load(raw_content)

# ===== 从环境变量读取 BASE_URL =====
base_url = os.getenv("BASE_URL")
if not base_url:
    raise RuntimeError("BASE_URL environment variable not set")

updated = False

for user in config["users"]:
    token = user.get("token")
    if not token:
        print(f"[SKIP] {user['name']}: token is empty")
        continue

    cookie = user.get("cookie")
    if not cookie:
        print(f"[SKIP] {user['name']}: cookie is empty, please login and fill in cookie first")
        continue

    # 先检查 token 是否仍然有效
    check_resp = requests.get(
        f"{base_url}/api/v1/sys/users/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if check_resp.status_code == 200:
        print(f"[OK] {user['name']}: token is still valid")
        continue

    # token 失效，尝试刷新
    print(f"[REFRESH] {user['name']}: token expired (status={check_resp.status_code}), refreshing...")
    try:
        resp = requests.post(
            f"{base_url}/api/v1/auth/refresh",
            headers={
                "Authorization": f"Bearer {token}",
                "Cookie": cookie
            },
            timeout=10
        )
        resp.raise_for_status()

        new_token = resp.json()["data"]["access_token"]

        # 从响应的 Set-Cookie 中提取新的 refresh_token
        new_cookie = None
        set_cookie = resp.headers.get("Set-Cookie", "")
        match = re.search(r"(emobody_refresh_token=[^;]+)", set_cookie)
        if match:
            new_cookie = match.group(1)

        # 只替换该用户的 token 值，保留文件其他内容（包括注释）
        raw_content = re.sub(
            r"(- name: " + re.escape(user["name"]) + r"\s+token: )(.+)",
            r"\g<1>" + new_token,
            raw_content
        )

        # 同时更新 cookie
        if new_cookie:
            raw_content = re.sub(
                r"(- name: " + re.escape(user["name"]) + r"\s+token: .+\n\s+cookie: )(.+)",
                r"\g<1>" + new_cookie,
                raw_content
            )

        updated = True
        print(f"[OK] {user['name']}: token refreshed successfully")
    except Exception as e:
        print(f"[ERROR] {user['name']}: failed to refresh token: {e}")

# 只在有更新时写回文件
if updated:
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        f.write(raw_content)
    print("\n[DONE] users.yml updated with new tokens")
else:
    print("\n[DONE] no tokens needed refreshing")
