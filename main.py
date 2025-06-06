from fastapi import FastAPI
from rag.rag import getAnswer

app = FastAPI()

@app.get("/get_answer")
def get_answer(query: str):
    return {"answer": getAnswer(query)}