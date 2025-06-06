import json
import re
from scrapy import Selector
from typing import List, Dict
import os

INPUT_FILE = 'data/angelone_support_content.json'
OUTPUT_FILE = 'data/angelone_faq_pairs.json'

def clean_text(text: str) -> str:
    """
    Clean and normalize text by removing extra whitespace and formatting
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove any remaining HTML entities
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    
    return text

def extract_faq_pairs_from_html(html_content: str) -> List[Dict[str, str]]:
    """
    Extract question-answer pairs from HTML content using Scrapy selectors
    """
    if not html_content:
        return []
    
    selector = Selector(text=html_content)
    faq_pairs = []
    
    # Find all tab structures
    tabs = selector.css('div.tab')
    
    for tab in tabs:
        # Extract question from label span
        question = tab.css('label.tab-label span::text').get()
        if question:
            question = clean_text(question)
            
            # Extract answer from tab-content
            content_div = tab.css('div.tab-content div.content')
            answer_parts = []
            if content_div:
                # Process all child elements in chronological order
                for element in content_div.css('*'):
                    tag_name = element.root.tag
                    
                    if tag_name == 'p':
                        text = clean_text(element.css('::text').get() or '')
                        if text:
                            answer_parts.append(text)
                    
                    elif tag_name == 'li':
                        text = clean_text(element.css('::text').get() or '')
                        if text:
                            answer_parts.append(f"• {text}")
            
            answer = '\n'.join(answer_parts)
            
            if answer:
                faq_pairs.append({
                    'question': question,
                    'answer': answer,
                })
    
    return faq_pairs

def process_content_file():
    """
    Process the scraped content file and extract all Q&A pairs
    """
    # Load the scraped content
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content_data = json.load(f)
    
    all_faq_pairs = []
    
    for item in content_data:
        url = item['url']
        html_content = item.get('content', '')
        
        if html_content:
            faq_pairs = extract_faq_pairs_from_html(html_content)
            all_faq_pairs.append({'url': url, 'faq_pairs': faq_pairs})
            print(f"Extracted {len(faq_pairs)} Q&A pairs from {url}")
        else:
            print(f"No content found for URL: {url}")
    
    # Save the extracted Q&A pairs
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_faq_pairs, f, indent=2, ensure_ascii=False)
    
    print(f"\nExtraction complete!")
    print(f"Total FAQ pairs extracted: {len(all_faq_pairs)}")
    print(f"Saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_content_file() 