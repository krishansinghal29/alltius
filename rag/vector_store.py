from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from typing import List

import json

load_dotenv()

class VectorStore:
    def __init__(self):
        self.angelone_vector_store_directory = "data/vector_store_angelone"
        self.insurance_vector_store_directory = "data/vector_store_insurance"
        self.embeddings = OpenAIEmbeddings()
        self.plans_path = "data/plans_final.json"
        self.additional_notes_path = "data/additional_notes.txt"
        self.angelone_faq_pairs_path = "data/angelone_faq_pairs.json"

    def _load_angelone_faq_pairs(self) -> List[Document]:
        """Load angelone faq pairs from json file and convert to documents."""
        with open(self.angelone_faq_pairs_path, 'r', encoding='utf-8') as f:
            faq_data = json.load(f)
        
        documents = []
        for entry in faq_data:
            url = entry['url']
            for faq in entry['faq_pairs']:
                question = faq['question']
                answer = faq['answer']
                content = f"Question\n{question}\nAnswer\n{answer}"
                metadata = {"source": url}
                documents.append(Document(page_content=content, metadata=metadata))
        
        # print(documents[0])
        return documents
    
    def _load_additional_notes(self) -> List[Document]:
        """Load additional notes from txt file and convert to documents."""
        with open(self.additional_notes_path, 'r', encoding='utf-8') as f:
            notes_data = f.read()
        
        documents = []
        # Split the text by double newlines to separate each document
        notes_list = notes_data.split('\n\n')
        for note in notes_list:
            content = note.strip()
            if content:
                metadata = {"source": "additional notes"}
                documents.append(Document(page_content=content, metadata=metadata))
        
        # print(len(documents))
        return documents
    
    def _load_plans(self) -> List[Document]:
        """Load plans from json file and convert to documents."""
        with open(self.plans_path, 'r', encoding='utf-8') as f:
            plans_data = json.load(f)
        
        documents = []
        for plan in plans_data:
            plan_name = plan["plan details"]["plan name"]
            
            # Process important questions
            for question_data in plan["important questions"]:
                content = f"""Start of information for Plan: {plan_name}
                "plan details": {plan["plan details"]["plan details"]}
                "question": {question_data["question"]}
                "answer": {question_data["answer"]}
                "why it matters": {question_data["why it matters"]}
                End of information for Plan: {plan_name}"""
                document = Document(page_content=content, metadata={"source": "plans", "type": "important_questions"})
                documents.append(document)
                # print(document)
                # break;
            
            # Process common medical events
            for event in plan["common medical events"]:
                for service in event["services"]:
                    content = f"""Start of information for Plan: {plan_name}
                    "plan details": {plan["plan details"]["plan details"]}
                    "event": {event["event category"]}
                    "service": {service["service name"]}
                    "member out of pocket": {service["member out of pocket"]}
                    "limitations and exceptions": {service["limitations and exceptions"]}
                    End of information for Plan: {plan_name}"""
                    document = Document(page_content=content, metadata={"source": "plans", "type": "medical_events"})
                    documents.append(document)
                #     print(document)
                #     break;
                # break;
            
            # Process excluded and covered services
            excluded_services = ", ".join(plan["excluded services"])
            other_covered = ", ".join(plan["other covered services"])
            content = f"""Start of information for Plan: {plan_name}
            "plan details": {plan["plan details"]["plan details"]}
            The following services are excluded in the plan: {excluded_services}
            Other covered services available with plan: {other_covered}
            End of information for Plan: {plan_name}"""
            document = Document(page_content=content, metadata={"source": "plans", "type": "others"})
            documents.append(document)
            # print(document)
            # break;
        
        return documents

    def _create_angelone_splits(self) -> List[Document]:
        """Load data from all the sources and convert to documents."""
        return self._load_angelone_faq_pairs()
    
    def _create_insurance_splits(self) -> List[Document]:
        """Load data from all the sources and convert to documents."""
        documents = self._load_plans()
        documents.extend(self._load_additional_notes())
        return documents

    def create_vector_store(self) -> None:
        """Create and persist a new vector store from documents."""
        splits = self._create_angelone_splits()
        Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.angelone_vector_store_directory
        )

        splits = self._create_insurance_splits()
        Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
            persist_directory=self.insurance_vector_store_directory
        )

if __name__ == "__main__":
    vector_store = VectorStore()
    vector_store.create_vector_store()