import requests

url = "http://localhost:8000/api/group/raw"
text = "主诊断：S01.800x011 其他诊断：S21.100x002 年龄：35岁"

response = requests.post(url, data=text.encode("utf-8"), headers={"Content-Type": "text/plain"})
print("状态码:", response.status_code)
print("返回结果:", response.json())