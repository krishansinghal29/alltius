from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class LLM:
    def __init__(self, model: str = "gpt-4.1-mini"):
        self.client = OpenAI()
        self.model = model

    def generate_response(self, user_message: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=[{"role": "user", "content": [{"type": "input_text", "text": user_message}]}]
        )
        return response.output_text
    
    def generate_structured_response(self, user_message: str, schema: BaseModel) -> BaseModel:
        response = self.client.responses.parse(
            model=self.model,
            input=[{"role": "user", "content": [{"type": "input_text", "text": user_message}]}],
            text_format=schema,
        )

        return response.output_parsed