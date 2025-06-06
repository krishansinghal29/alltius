from fastapi import FastAPI
from rag.rag import getAnswer

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/get_answer")
def get_answer(query: str):
    return {"answer": getAnswer(query)}