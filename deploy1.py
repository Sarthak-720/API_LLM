from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from langserve import add_routes
from Gemini_LLM import ChatGemini

# Define input schema for request body
class InputModel(BaseModel):
    input: dict

app = FastAPI(
    title="Gemini Server",
    version="1.0",
    description="API server using Gemini via LangChain.",
)

generation_config = {
    "temperature": 0.4,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 2048,
    "response_mime_type": "text/plain",
}
gemini_model = ChatGemini(
    model_name="gemini-1.5-flash",
    credentials_path=r"C:\Users\SARTHAK\Downloads\intern-project-446606-598b57e7913a.json",
    generation_config=generation_config,
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Gemini Server"}

@app.post("/invoke")
async def invoke_model(input_model: InputModel):
    try:
        topic = input_model.input.get("topic")
        if not topic:
            raise ValueError("Missing 'topic' in request payload")
        
        result = gemini_model.invoke(topic)  # Call LLM
        return {"output": result}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid request: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
