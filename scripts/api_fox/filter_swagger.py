import requests
import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

SOURCE_SWAGGER_URL = os.getenv("SOURCE_SWAGGER_URL")
REMOVE_TAGS = os.getenv("REMOVE_TAGS", "")

OUTPUT_FILE = "swagger_filtered.json"

REMOVE_TAG_LIST = [t.strip() for t in REMOVE_TAGS.split(",") if t.strip()]


def fetch_swagger():
    if not SOURCE_SWAGGER_URL:
        print("SOURCE_SWAGGER_URL not set")
        sys.exit(1)

    print(f"Downloading swagger from: {SOURCE_SWAGGER_URL}")
    resp = requests.get(SOURCE_SWAGGER_URL, timeout=60)
    resp.raise_for_status()
    return resp.json()


def filter_swagger(data):
    if not REMOVE_TAG_LIST:
        print("No REMOVE_TAGS configured, skip filtering.")
        return data

    print(f"Filtering tags: {REMOVE_TAG_LIST}")

    new_paths = {}

    for path, methods in data.get("paths", {}).items():
        new_methods = {}

        for method, detail in methods.items():
            tags = detail.get("tags", [])

            if any(tag in REMOVE_TAG_LIST for tag in tags):
                continue

            new_methods[method] = detail

        if new_methods:
            new_paths[path] = new_methods

    data["paths"] = new_paths
    return data


def main():
    swagger = fetch_swagger()
    filtered = filter_swagger(swagger)

    content = json.dumps(filtered, ensure_ascii=False, indent=2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Swagger written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
