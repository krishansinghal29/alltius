import scrapy
import json
import os
from typing import Generator, Dict, Any

OUTPUT_FILE = 'data/angelone_support_content.json'
INPUT_FILE = 'data/angelone_support_urls_final.txt'

class ContentFetcher(scrapy.Spider):
    name = 'angelone_content_fetcher'
    allowed_domains = ['angelone.in']
    
    def __init__(self, *args, **kwargs):
        super(ContentFetcher, self).__init__(*args, **kwargs)
        self.scraped_content = []
        
    def start_requests(self):
        """
        Read URLs from the filtered file and create requests for each URL
        """
        if not os.path.exists(INPUT_FILE):
            self.logger.error(f"Input file {INPUT_FILE} not found!")
            return
            
        with open(INPUT_FILE, 'r') as f:
            urls = [line.strip() for line in f.readlines() if line.strip()]
        
        self.logger.info(f"Found {len(urls)} URLs to scrape")
        
        for url in urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_content,
                errback=self.handle_error
            )
    
    def parse_content(self, response) -> Generator[Dict[str, Any], None, None]:
        """
        Extract raw HTML content from each page
        """
        self.logger.info(f'Scraping content from: {response.url}')

        content = response.css('.list-content').get()

        if content:
            self.logger.info(f'Content extracted from: {response.url}')
        else:
            self.logger.warning(f'No content found at the specified selector for: {response.url}')
        
        # Create content item with raw HTML
        content_item = {
            'url': response.url,
            'content': content,
            'scraped_at': response.meta.get('download_time', '').isoformat() if response.meta.get('download_time') else None
        }
        
        self.scraped_content.append(content_item)
        
        yield content_item
    
    def handle_error(self, failure):
        """
        Handle request errors
        """
        self.logger.error(f'Request failed for {failure.request.url}: {failure.value}')
        
        # Still create an entry for failed requests
        error_item = {
            'url': failure.request.url,
            'error': str(failure.value),
            'status_code': getattr(failure.value, 'response', {}).get('status', None) if hasattr(failure.value, 'response') else None,
            'scraped_at': None
        }
        
        self.scraped_content.append(error_item)
        yield error_item
    
    def closed(self, reason):
        """
        Called when the spider closes. Save all content to JSON file.
        """
        self.logger.info(f'Spider closed: {reason}')
        self.logger.info(f'Total pages processed: {len(self.scraped_content)}')
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        
        # Save all scraped content to JSON file
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_content, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f'All content saved to {OUTPUT_FILE}')
        
        # Print summary statistics
        successful_scrapes = sum(1 for item in self.scraped_content if 'error' not in item)
        failed_scrapes = sum(1 for item in self.scraped_content if 'error' in item)
        
        self.logger.info(f'Summary:')
        self.logger.info(f'  Successful scrapes: {successful_scrapes}')
        self.logger.info(f'  Failed scrapes: {failed_scrapes}')
