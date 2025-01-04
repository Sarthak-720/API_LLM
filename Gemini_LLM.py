from langchain.schema import LLMResult
from langchain.schema.messages import AIMessage, HumanMessage
import google.generativeai as genai
from langchain_core.runnables import Runnable
import os

from langchain_core.runnables import Runnable
from langchain.schema import AIMessage, ChatMessage, HumanMessage, ChatResult

class ChatGemini(Runnable):
    def __init__(self, model_name: str, credentials_path: str, generation_config: dict):

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        self.model = genai.GenerativeModel(
            model_name=model_name, 
            generation_config=generation_config
        )

    def invoke(self, input_data: list[ChatMessage]) -> ChatResult:

        prompt = "\n".join([msg.content for msg in input_data if isinstance(msg, HumanMessage)])

        chat_session = self.model.start_chat(history=[])
        response = chat_session.send_message(prompt)

        ai_message = AIMessage(content=response.text)
        return ChatResult(messages=[ai_message])
