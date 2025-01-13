import base64
import json
import os
import google.generativeai as genai
from cryptography.fernet import Fernet
class ChatGemini:
    def __init__(self, model_name: str, credentials_path: str, generation_config: dict):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        genai.configure(api_key="AIzaSyCdCy_pq1b4m3OT2OfNWQr4XJ46LD4xVqM")  # Replace with your API key
        self.model = genai.GenerativeModel(
            model_name=model_name, 
            generation_config=generation_config
        )

    def invoke(self, input_data) -> dict:
        try:
        # Parse input
            payload = json.loads(input_data[0].content)
            encrypted_csv = payload.get("encrypted_csv")
            password = payload.get("password")
            user_task = payload.get("topic")

            if not encrypted_csv or not password or not user_task:
                raise ValueError("Missing required data")

        # Decrypt CSV data
            cipher = Fernet(password.encode())
            decrypted_csv_data = cipher.decrypt(encrypted_csv.encode())

        # Load CSV into Pandas
            csv_data_path = "temp_decrypted.csv"
            with open(csv_data_path, "wb") as file:
                file.write(decrypted_csv_data)

            data = pd.read_csv(csv_data_path)
            os.remove(csv_data_path)

        # Prepare prompt
            csv_data_str = data.to_string(index=False)
            prompt = f"Task: {user_task}\n\nRelevant CSV Data:\n{csv_data_str}"

        # Send prompt to LLM
            chat_session = self.start_chat_session()
            response = chat_session.send_message(prompt)

        # Re-encrypt processed response
            encrypted_response = cipher.encrypt(response.text.encode())

            return {
            "response": encrypted_response.decode(),  # Send encrypted response
            "status": "success",
            }

        except Exception as e:
            return {"response": str(e), "status": "failed"}


    def start_chat_session(self):
        return self.model.start_chat(history=[])
