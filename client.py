import requests

def format_response(text):
    # Remove asterisks and clean up the formatting
    lines = text.split('\n')
    formatted_lines = []
    
    for line in lines:
        # Remove asterisks used for bold formatting
        line = line.replace('**', '')
        
        # Handle bullet points
        if line.strip().startswith('*'):
            # Replace * with • and add proper indentation
            line = '  • ' + line.strip()[1:].strip()
            
        formatted_lines.append(line)
    
    # Join the lines back together
    return '\n'.join(formatted_lines)

url = "http://localhost:8000/gemini"
topic = str(input("Enter topic: "))
payload = {"topic": topic}
headers = {"Content-Type": "application/json"}

# print("Payload being sent:", payload)

try:
    response = requests.post(url, json=payload, headers=headers)
    print("Status Code:", response.status_code)
    if response.status_code == 200:
        result = response.json()
        print("Keys in response JSON:", result.keys())  
        
        if "response" in result:
            formatted_text = format_response(result["response"])
            print("\nResponse:")
            print("-" * 80)  
            print(formatted_text)
            print("-" * 80)  
        else:
            print("Response is not included in the result.")
    else:
        print("Error:", response.json())
except requests.exceptions.RequestException as e:
    print("An error occurred:", e)
