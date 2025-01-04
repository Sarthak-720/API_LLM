import requests

url = "http://localhost:8000/invoke"
topic = str(input("Enter topic: "))
payload = {"input": {"topic": topic}}
headers = {"Content-Type": "application/json"}

print("Payload being sent:", payload)  # Debugging step

try:
    response = requests.post(url, json=payload, headers=headers)
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except requests.exceptions.RequestException as e:
    print("An error occurred:", e)
