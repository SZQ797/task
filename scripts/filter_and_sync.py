import requests
import json
import hashlib
import sys
import time
import os
from dotenv import load_dotenv

# 自动加载本地 .env（CI 环境不存在该文件不会报错）
load_dotenv()

SOURCE_SWAGGER_URL = os.getenv("SOURCE_SWAGGER_URL")
APIFOX_TOKEN = os.getenv("APIFOX_TOKEN")
REMOVE_TAGS = os.getenv("REMOVE_TAGS", "")

# APIFox接口文档：https://apifox-openapi.apifox.cn/api-173409873
APIFOX_PROJECT_ID = "6303814"

# 用于存储或匹配 API 接口的目标目录的 ID。如果未指定，目标目录将为 Root 目录
APIFOX_ENDPOINT_FOLDER_ID = 78511592

#用于存储或匹配数据模型的目标目录的 ID。如果未指定，目标目录将为 Root 目录
APIFOX_SCHEMA_FOLDER_ID = 18424983

APIFOX_API_VERSION = "2024-03-28"

OUTPUT_FILE = "swagger_filtered.json"
# =============================


# 多模块名解析
REMOVE_TAG_LIST = [t.strip() for t in REMOVE_TAGS.split(",") if t.strip()]


def fetch_swagger():
    if not SOURCE_SWAGGER_URL:
        print("SOURCE_SWAGGER_URL not set")
        sys.exit(1)

    resp = requests.get(SOURCE_SWAGGER_URL, timeout=60)
    resp.raise_for_status()
    return resp.json()


def filter_swagger(data):
    if not REMOVE_TAG_LIST:
        print("No REMOVE_TAGS configured, skip filtering.")
        return data

    new_paths = {}

    for path, methods in data.get("paths", {}).items():
        new_methods = {}

        for method, detail in methods.items():
            tags = detail.get("tags", [])

            # 如果接口的 tag 在删除列表中，则跳过
            if any(tag in REMOVE_TAG_LIST for tag in tags):
                continue

            new_methods[method] = detail

        if new_methods:
            new_paths[path] = new_methods

    data["paths"] = new_paths
    return data


def calculate_hash(content):
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def write_if_changed(content):
    new_hash = calculate_hash(content)

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            old_content = f.read()
        old_hash = calculate_hash(old_content)

        if old_hash == new_hash:
            print("Swagger has no changes.")
            # return False

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print("Swagger updated.")
    return True


def sync_to_apifox(content):
    if not APIFOX_TOKEN:
        print("APIFOX_TOKEN not set")
        sys.exit(1)

    api_url = f"https://api.apifox.com/v1/projects/{APIFOX_PROJECT_ID}/import-openapi?locale=zh-CN"

    headers = {
        "Content-Type": "application/json",
        "X-Apifox-Api-Version": APIFOX_API_VERSION,
        "Authorization": f"Bearer {APIFOX_TOKEN}",
    }

    payload = {
        "input": {
            "content": content
        },
        "options": {
            "targetEndpointFolderId": APIFOX_ENDPOINT_FOLDER_ID,
            "targetSchemaFolderId": APIFOX_SCHEMA_FOLDER_ID,
            "endpointOverwriteBehavior": "AUTO_MERGE",
            "deleteUnmatchedResources": False,
            "schemaOverwriteBehavior": "AUTO_MERGE",
            "updateFolderOfChangedEndpoint": True,
            "prependBasePath": False
        }
    }

    resp = requests.post(api_url, headers=headers, json=payload, timeout=60)

    if resp.status_code != 200:
        print("Apifox sync failed:")
        print(resp.text)
        sys.exit(1)

    print("Apifox sync success.")



def main():
    print("Fetching swagger...")
    swagger = fetch_swagger()

    print("Filtering swagger by tags:", REMOVE_TAG_LIST)
    filtered = filter_swagger(swagger)

    content = json.dumps(filtered, ensure_ascii=False, indent=2)

    changed = write_if_changed(content)

    if not changed:
        print("Skip sync because no changes.")
        return

    print("Syncing to Apifox...")
    sync_to_apifox(content)



if __name__ == "__main__":
    main()
