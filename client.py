import requests

url = "http://localhost:8000/invoke"
topic = str(input())
payload = {"input": {"topic": topic}}
headers = {"Content-Type": "application/json"}

response = requests.post(url, json=payload, headers=headers)
print("Status Code:", response.status_code)
print("Response:", response.json())