import scrapy
# from spiders.url_finder import UrlFinder
from spiders.fetch_content import ContentFetcher

# Utility class to run the spider programmatically
class AngelOneSupportScraper:
    """
    A wrapper class to run the AngelOne support spider programmatically.
    """
    
    def __init__(self, spider_class: scrapy.Spider):
        self.spider_class = spider_class
        
    def run_spider(self, output_file: str = 'data/debug/angelone_support_pages.json'):
        """
        Run the spider and save results to a file.
        
        Args:
            output_file: Name of the output file to save scraped data
        """
        from scrapy.crawler import CrawlerProcess
        from scrapy.utils.project import get_project_settings
        
        # Configure settings
        settings = get_project_settings()
        settings.update({
            'FEEDS': {
                output_file: {
                    'format': 'json',
                    'overwrite': True,
                },
            },
            'ROBOTSTXT_OBEY': False,  # Respect robots.txt
            'DOWNLOAD_DELAY': 1,     # Be polite - 1 second delay between requests
            'RANDOMIZE_DOWNLOAD_DELAY': 0.5,  # Randomize delay (0.5 * to 1.5 * DOWNLOAD_DELAY)
            'CONCURRENT_REQUESTS': 16,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 8,
            'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        })
        
        # Create and start the crawler
        process = CrawlerProcess(settings)
        process.crawl(self.spider_class)
        process.start()


# Example usage
if __name__ == '__main__':
    # scraper = AngelOneSupportScraper(UrlFetcher)
    scraper = AngelOneSupportScraper(ContentFetcher)
    scraper.run_spider('data/debug/angelone_contentfetcher.json')
