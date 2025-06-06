from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_chroma import Chroma
from typing import List
from openai import OpenAI

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
        self.client = OpenAI()
        self.model = "gpt-4.1-mini"

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
"""

        return prompt
    
    def generate_answer(self, query: str, documents: List[Document]) -> str:
        """Generate an answer to a given query using the retrieved documents."""
        user_prompt = self._generate_user_prompt(query, documents)
        # print(user_prompt)
        response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_text",
                                "text": user_prompt,
                            },
                        ]
                    }
                ]
            )
        return response.output_text

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

if __name__ == "__main__":
    print(queryAngelOne("How can I withdraw my money?"))