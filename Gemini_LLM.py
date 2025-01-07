from langchain.schema import AIMessage, ChatMessage, HumanMessage, ChatResult
import google.generativeai as genai
from langchain_core.runnables import Runnable
import os
import pandas as pd


class ChatGemini(Runnable):
    # Predetermined path for the CSV file
    CSV_PATH = "path_to_your_file.csv"

    def __init__(self, model_name: str, credentials_path: str, generation_config: dict):
        """
        Initialize the ChatGemini class with an LLM and a predetermined CSV file.

        Args:
            model_name (str): The name of the LLM model.
            credentials_path (str): Path to the Google credentials file.
            generation_config (dict): Configuration for the LLM generation.
        """
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # Initialize the Google Generative AI model
        self.model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )

        # Load and preprocess the predetermined CSV file
        self.data = self._load_and_preprocess_csv()

    @staticmethod
    def _load_and_preprocess_csv() -> pd.DataFrame:
        """
        Load and preprocess the CSV file from the predetermined path.

        Returns:
            pd.DataFrame: Preprocessed DataFrame.
        """
        # Load the CSV file
        data = pd.read_csv(ChatGemini.CSV_PATH)

        # Example preprocessing: drop missing values and reset the index
        data = data.dropna().reset_index(drop=True)

        # Add more preprocessing steps as needed
        return data

    def invoke(self, input_data: list[ChatMessage]) -> ChatResult:
        """
        Process the user's query with the pre-processed CSV data and the LLM.

        Args:
            input_data (list[ChatMessage]): List of user messages.

        Returns:
            ChatResult: AI response after analyzing the data.
        """
        # Extract the user's query
        prompt = "\n".join([msg.content for msg in input_data if isinstance(msg, HumanMessage)])

        # Combine the preprocessed data and user query for analysis
        llm_input = (
            f"You are a data assistant. The following is the data extracted from a CSV file:\n"
            f"{self.data.to_string(index=False)}\n\n"
            f"User's request: {prompt}\n\n"
            f"Perform the requested analysis or task based on the data."
        )

        # Generate a response using the LLM
        chat_session = self.model.start_chat(history=[])
        response = chat_session.send_message(llm_input)

        ai_message = AIMessage(content=response.text)
        return ChatResult(messages=[ai_message])
