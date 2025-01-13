from fastapi import FastAPI, HTTPException
from Gemini_LLM import ChatGemini
from langchain.schema.messages import HumanMessage
from cryptography.fernet import Fernet
import base64
import os
import json
# Path to CSV and key file
CSV_DATA_PATH = r"C:\Users\SARTHAK\Downloads\Results_lm.csv"
KEY_FILE = "secret.key"

# Key management
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)

def load_key():
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()

generate_key()
key = load_key()
cipher = Fernet(key)

# Encrypt the CSV file
def encrypt_csv(file_path):
    with open(file_path, "rb") as file:
        encrypted_data = cipher.encrypt(file.read())
        print(encrypted_data)
    return encrypted_data

encrypted_csv = encrypt_csv(CSV_DATA_PATH)

# FastAPI app setup
app = FastAPI(
    title="Gemini Server",
    version="1.0",
    description="API server using Gemini via LangChain.",
)

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
gemini_model = ChatGemini(
    model_name="gemini-1.5-flash",
    credentials_path="C:\\Users\\SARTHAK\\Downloads\\gen-lang-client-0091686678-84db239ad662.json",
    generation_config=generation_config,
)

@app.post("/gemini")
async def invoke_gemini(input: dict):
    try:
        topic = input.get("topic", "").strip()

        if not topic:
            raise ValueError("Topic cannot be empty")

        payload = {
            "encrypted_csv": encrypted_csv.decode(),
            "password": key.decode(), 
            "topic": topic
        }

        payload_json = json.dumps(payload)

        result = gemini_model.invoke([HumanMessage(content=payload_json)])

        encrypted_response = result.get("response", "").encode()
        decrypted_response = cipher.decrypt(encrypted_response).decode()

        response = {
            "response": decrypted_response,  
            "status": result.get("status", "failed"),
        }
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
