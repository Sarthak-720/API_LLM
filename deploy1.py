from fastapi import FastAPI
from langserve import add_routes
from Gemini_LLM import ChatGemini  # Assuming your wrapper is saved in llm.py

app = FastAPI(
    title="Gemini Server",
    version="1.0",
    description="API server using Gemini via LangChain.",
)

# Define Gemini configuration
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

# Add routes for Gemini
add_routes(app, gemini_model, path="/gemini")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)