import os
import json
import urllib.request

url = "https://test-app.emobody.cn/api/v1/auth/sms/send"

headers = {
    "User-Agent": "Apifox/1.0.0 (https://apifox.com)",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Host": "test-app.emobody.cn",
    "Connection": "keep-alive",
}

# 从 GitHub Secret 读取手机号
phone = os.getenv("PHONE_NUMBER")
if not phone:
    raise ValueError("请在 GitHub Secrets 中设置 PHONE_NUMBER")

data = {
    "phone": phone,
    "method": "login"
}

req = urllib.request.Request(
    url=url,
    data=json.dumps(data).encode("utf-8"),
    headers=headers,
    method="POST"
)

with urllib.request.urlopen(req, timeout=10) as resp:
    body = resp.read().decode("utf-8")
    print("status:", resp.status)
    print("response:", body)
