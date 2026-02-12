import os
import requests
import sys
from dotenv import load_dotenv

load_dotenv()

APIFOX_TOKEN = os.getenv("APIFOX_TOKEN")

# APIFox接口文档：https://apifox-openapi.apifox.cn/api-173409873
APIFOX_PROJECT_ID = "6303814"

# 用于存储或匹配 API 接口的目标目录的 ID。如果未指定，目标目录将为 Root 目录
APIFOX_ENDPOINT_FOLDER_ID = 78522823

#用于存储或匹配数据模型的目标目录的 ID。如果未指定，目标目录将为 Root 目录
APIFOX_SCHEMA_FOLDER_ID = 18428082

APIFOX_API_VERSION = "2024-03-28"

OUTPUT_FILE = "swagger_filtered.json"


def main():
    if not APIFOX_TOKEN:
        print("APIFOX_TOKEN not set")
        sys.exit(1)

    repo = os.getenv("GITHUB_REPOSITORY")

    if not repo:
        print("GITHUB_REPOSITORY not found")
        sys.exit(1)

    raw_url = f"https://raw.githubusercontent.com/{repo}/main/{OUTPUT_FILE}"

    api_url = (
        f"https://api.apifox.com/v1/projects/"
        f"{APIFOX_PROJECT_ID}/import-openapi?locale=zh-CN"
    )

    headers = {
        "Content-Type": "application/json",
        "X-Apifox-Api-Version": APIFOX_API_VERSION,
        "Authorization": f"Bearer {APIFOX_TOKEN}",
    }

    payload = {
        "input": {
            "url": raw_url
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

    print(f"Syncing from URL: {raw_url}")

    resp = requests.post(api_url, headers=headers, json=payload, timeout=60)

    if resp.status_code != 200:
        print("Apifox sync failed:")
        print(resp.text)
        sys.exit(1)

    print("Apifox sync success.")


if __name__ == "__main__":
    main()
