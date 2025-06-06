from urllib.parse import urlparse, urlunparse
from typing import Set, List

class AngelOneUrlFilter:
    """
    A class to filter AngelOne support URLs, removing duplicates and Hindi language variants.
    
    Features:
    - Removes URLs containing '/hindi/' after '/support'
    - Removes duplicate URLs that only differ by hash fragments (#head-*)
    - Preserves the original order where possible
    """
    
    def __init__(self, input_file: str = "data/angelone_support_urls.txt"):
        """
        Initialize the URL filter with the input file path.
        
        Args:
            input_file (str): Path to the file containing URLs to filter
        """
        self.input_file = input_file
        self.filtered_urls: List[str] = []
        
    def read_urls(self) -> List[str]:
        """
        Read URLs from the input file.
        
        Returns:
            List[str]: List of URLs from the file
        """
        try:
            with open(self.input_file, 'r', encoding='utf-8') as file:
                urls = [line.strip() for line in file if line.strip()]
            return urls
        except FileNotFoundError:
            print(f"Error: File {self.input_file} not found.")
            return []
    
    def is_hindi_url(self, url: str) -> bool:
        """
        Check if a URL contains '/hindi/' after '/support'.
        
        Args:
            url (str): The URL to check
            
        Returns:
            bool: True if the URL contains Hindi language path, False otherwise
        """
        return '/support/hindi/' in url
    
    def get_base_url(self, url: str) -> str:
        """
        Get the base URL without hash fragments.
        
        Args:
            url (str): The full URL
            
        Returns:
            str: URL without hash fragment
        """
        parsed = urlparse(url)
        # Remove the fragment (hash) part
        base_parsed = parsed._replace(fragment='')
        return urlunparse(base_parsed)
    
    def filter_urls(self) -> List[str]:
        """
        Filter the URLs by removing Hindi variants and duplicates.
        
        Returns:
            List[str]: Filtered list of unique URLs
        """
        urls = self.read_urls()
        print(f'Read {len(urls)} URLs')

        if not urls:
            return []
        
        seen_base_urls: Set[str] = set()
        filtered_urls: List[str] = []
        
        for url in urls:
            # Skip Hindi URLs
            if self.is_hindi_url(url):
                continue
            
            # Get base URL without hash fragments
            base_url = self.get_base_url(url)
            
            # Only add if we haven't seen this base URL before
            if base_url not in seen_base_urls:
                seen_base_urls.add(base_url)
                filtered_urls.append(base_url)
        
        print(f'Filtered {len(filtered_urls)} URLs')
        self.filtered_urls = filtered_urls
        return filtered_urls
    
    def save_filtered_urls(self, output_file: str = "data/angelone_support_urls_filtered.txt") -> bool:
        """
        Save the filtered URLs to a new file.
        
        Args:
            output_file (str): Path to save the filtered URLs
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.filtered_urls:
            self.filter_urls()
        
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                for url in self.filtered_urls:
                    file.write(url + '\n')
            print(f"Filtered URLs saved to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving filtered URLs: {e}")
            return False


def main():
    """Example usage of the AngelOneUrlFilter class."""
    # Initialize the filter
    url_filter = AngelOneUrlFilter()
    
    # Filter URLs
    filtered_urls = url_filter.filter_urls()
    # Save filtered URLs
    url_filter.save_filtered_urls()


if __name__ == "__main__":
    main() 