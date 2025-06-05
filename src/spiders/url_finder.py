import scrapy
from urllib.parse import urljoin, urlparse
from typing import Set, Generator

OUTPUT_FILE = 'data/angelone_support_urls1.json'

class UrlFinder(scrapy.Spider):
    name = 'angelone_support'
    allowed_domains = ['angelone.in']
    start_urls = ['https://www.angelone.in/support']
    
    def __init__(self, *args, **kwargs):
        super(UrlFinder, self).__init__(*args, **kwargs)
        self.found_urls: Set[str] = set()
        self.base_url = 'https://www.angelone.in/support'
    
    def parse(self, response) -> Generator:
        """
        Main parsing method that extracts all links and follows them
        if they're under the support section.
        """
        # Add current URL to found URLs
        current_url = response.url
        self.found_urls.add(current_url)

        yield {
            'url': current_url,
            'parent_url': None,
            'found_on_page': current_url
        }
        
        # Log the current page being processed
        self.logger.info(f'Processing: {current_url}')
        
        # Extract all links from the page
        links = response.css('a::attr(href)').getall()
        
        for link in links:
            # Convert relative URLs to absolute URLs
            absolute_url = urljoin(response.url, link)
            
            # Check if the URL is under the support section
            if self.is_support_url(absolute_url) and absolute_url not in self.found_urls:
                self.found_urls.add(absolute_url)
                
                # Yield the URL as an item
                yield {
                    'url': absolute_url,
                    'parent_url': current_url,
                    'found_on_page': response.url
                }
                
                # Follow the link to crawl it recursively
                yield response.follow(absolute_url, self.parse)
    
    def is_support_url(self, url: str) -> bool:
        """
        Check if the given URL is under the support section.
        """
        parsed_url = urlparse(url)
        
        # Check if it's from the same domain
        if parsed_url.netloc not in ['www.angelone.in', 'angelone.in']:
            return False
        
        # Check if the path starts with /support
        if not parsed_url.path.startswith('/support'):
            return False
        
        # Exclude certain file types that might not be webpages
        excluded_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.zip', '.rar']
        if any(parsed_url.path.lower().endswith(ext) for ext in excluded_extensions):
            return False
        
        return True
    
    def closed(self, reason):
        """
        Called when the spider closes. Print summary of found URLs.
        """
        self.logger.info(f'Spider closed: {reason}')
        self.logger.info(f'Total URLs found: {len(self.found_urls)}')
        
        # Optionally, you can save all found URLs to a file
        with open(OUTPUT_FILE, 'w') as f:
            for url in sorted(self.found_urls):
                f.write(f'{url}\n')
        
        self.logger.info('All URLs saved to angelone_support_urls.txt')