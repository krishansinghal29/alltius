from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from typing import List
from llm import LLM
from pydantic import BaseModel

load_dotenv()

class RAG:
    def __init__(self, vector_store_directory: str):
        self.vector_store_directory = vector_store_directory
        self.retriever_k = 10
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = Chroma(
            persist_directory=self.vector_store_directory,
            embedding_function=self.embeddings
        )
        self.llm = LLM("gpt-4.1-mini")

    def retrieve_documents(self, query: str) -> List[Document]:
        """Retrieve relevant documents for a given query."""
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.retriever_k})
        return retriever.invoke(query)
    
    def _generate_user_prompt(self, query: str, documents: List[Document]) -> str:
        """Generate a user prompt for a given query and documents."""
        context = "\n".join([f"Document {i+1}:\n{doc.page_content}\n" for i, doc in enumerate(documents)])
        
        prompt = f"""Please answer the following question based STRICTLY on the provided documents. If the answer cannot be fully derived from the provided documents, respond with 'I don't know'.

Context Documents:
{context}

Question: {query}

Remember:
1. Only use information from the provided documents above
2. If the information is not in the documents, respond with 'I don't know'
3. Do not make assumptions or include external knowledge
4. Just state the answer, do not include as per Document 1, Document 2, etc.
5. If there are steps to be followed, state them in a list.
"""

        return prompt
    
    def generate_answer(self, query: str, documents: List[Document]) -> str:
        """Generate an answer to a given query using the retrieved documents."""
        user_prompt = self._generate_user_prompt(query, documents)
        print(user_prompt)
        return self.llm.generate_response(user_prompt)
    
def queryAngelOne(query: str) -> str:
    rag = RAG("data/vector_store_angelone")
    documents = rag.retrieve_documents(query)
    answer = rag.generate_answer(query, documents)
    return answer

def queryInsurance(query: str) -> str:
    rag = RAG("data/vector_store_insurance")
    documents = rag.retrieve_documents(query)
    answer = rag.generate_answer(query, documents)
    return answer

def getAnswer(query: str) -> str:
    llm = LLM("gpt-4.1-mini")
    prompt = f"""
    You are tasked with determining the category of a given query. The query will either be related to AngelOne, a stock buy and sell platform similar to Robinhood or Zerodha, or it will be related to an insurance plan.

    Query: {query}

    Instructions:
    1. Analyze the query to determine its context.
    2. If the query is related to stock trading, buying, selling, or any financial transactions typically associated with platforms like AngelOne, classify it as related to AngelOne.
    3. If the query pertains to insurance policies, coverage, claims, or any other insurance-related topics, classify it as related to insurance.
    4. Return True in the field 'isAngelOne' if the query is related to AngelOne, otherwise return False.
    """

    class OutputSchema(BaseModel):
        isAngelOne: bool

    isAngelOne = llm.generate_structured_response(prompt, OutputSchema)
    if isAngelOne.isAngelOne:
        return queryAngelOne(query)
    else:
        return queryInsurance(query)
    
if __name__ == "__main__":
    print(queryAngelOne("How can I withdraw my money?"))