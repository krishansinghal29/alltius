import json
from typing import Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class PDFParser:
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4.1"
        self.user_prompt = """
        You are an expert data extraction assistant. Your task is to parse the text content of a health insurance 'Summary of Benefits and Coverage' (SBC) document and convert it into a single, valid, and structured JSON object.

        Instructions:
        - Read the entire provided text from the SBC document.
        - Your output must be only the JSON object. Do not include any introductory text, explanations, or markdown formatting around the JSON block.
        - Adhere strictly to the JSON schema defined below. Do not add, remove, or rename any keys.
        - If a specific piece of information cannot be found in the document, use null as the value for string fields or an empty array [] for array fields.
        - Populate the keys with the corresponding data extracted from the document. Pay close attention to tables and lists.

        Use the following JSON schema:
        {
            "plan details": {
                "plan name": "String", // The name of the health plan, e.g., "PSM Health Plan: 2,500 Plan Option" 
                "coverage for": "String", 
                "plan type": "String" // The type of plan, e.g., "Traditional" 
            },
            "important questions": [
                {
                "question": "String", // The question from the 'Important Questions' table 
                "answer": "String", // The corresponding answer to the question 
                "why it matters": "String" // The explanation from the 'Why This Matters' column 
                }
            ],
            "common medical events": [
                {
                "event category": "String", // The main heading for the event, e.g., "If you visit a health care provider's office or clinic" 
                "services": [
                    {
                    "service name": "String", // The specific service, e.g., "Primary care visit to treat an injury or illness" 
                    "member out of pocket": "String", // The cost to the member, e.g., "$25 copay/visit" 
                    "limitations and exceptions": "String" // Any associated limitations or notes 
                    }
                ]
                }
            ],
            "excluded services": [
                "String" // A list of services that are explicitly not covered by the plan 
            ],
            "other covered services": [
                "String" // A list of other covered services that may have limitations 
            ],
        }
        """

    def parse_content(self, pdf_path: str) -> Dict[str, Any]:
        """Send content to OpenAI API for parsing."""
        try:
            file = self.client.files.create(
                file=open(pdf_path, "rb"),
                purpose="user_data"
            )

            response = self.client.responses.create(
                model=self.model,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_file",
                                "file_id": file.id,
                            },
                            {
                                "type": "input_text",
                                "text": self.user_prompt,
                            },
                        ]
                    }
                ]
            )
            
            json_str = response.output_text
            return json.loads(json_str)
            
        except Exception as e:
            raise Exception(f"Error parsing content with OpenAI: {str(e)}")

def main():
    # Example usage
    parser = PDFParser()
    
    # Replace with your PDF file path
    pdfs = ["data/insurance/America's_Choice_2500_Gold_SOB (1) (1).pdf",
            "data/insurance/America's_Choice_5000_Bronze_SOB (2).pdf",
            "data/insurance/America's_Choice_5000_HSA_SOB (2).pdf",
            "data/insurance/America's_Choice_7350_Copper_SOB (1) (1).pdf"]
    
    output_path = "data/plans.json"
    plans = []
    
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def process_pdf(pdf_path):
        try:
            result = parser.parse_content(pdf_path)
            print(f"Successfully parsed {pdf_path}")
            return result
        except Exception as e:
            print(f"Error: {str(e)}")
            return None

    with ThreadPoolExecutor() as executor:
        future_to_pdf = {executor.submit(process_pdf, pdf_path): pdf_path for pdf_path in pdfs}
        for future in as_completed(future_to_pdf):
            _ = future_to_pdf[future]
            result = future.result()
            if result is not None:
                plans.append(result)
    
    # Save to file if output path is provided
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(plans, f, indent=2)

if __name__ == "__main__":
    main()
