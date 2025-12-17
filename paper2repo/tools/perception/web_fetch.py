"""Web fetching tool for retrieving online content - no side effects."""
from typing import Dict, Any, Optional
import logging
import requests
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class WebFetch:
    """Tool for fetching web content."""
    
    def __init__(self, timeout: int = 30):
        """Initialize web fetch tool.
        
        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Paper2Repo/1.0 (Research Paper Processing)'
        })
    
    def fetch(self, url: str) -> Dict[str, Any]:
        """Fetch content from URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with fetched content and metadata
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            return {
                "url": url,
                "status_code": response.status_code,
                "content": response.text,
                "headers": dict(response.headers),
                "encoding": response.encoding,
                "success": True
            }
        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return {
                "url": url,
                "success": False,
                "error": str(e)
            }
    
    def fetch_paper_metadata(self, doi: str) -> Dict[str, Any]:
        """Fetch paper metadata from DOI.
        
        Args:
            doi: DOI of the paper
            
        Returns:
            Paper metadata
        """
        # Use CrossRef API
        url = f"https://api.crossref.org/works/{doi}"
        
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            message = data.get("message", {})
            
            return {
                "doi": doi,
                "title": message.get("title", [""])[0],
                "authors": [
                    {
                        "name": f"{author.get('given', '')} {author.get('family', '')}".strip()
                    }
                    for author in message.get("author", [])
                ],
                "published": message.get("published-print", {}).get("date-parts", [[None]])[0],
                "abstract": message.get("abstract", ""),
                "url": message.get("URL", ""),
                "success": True
            }
        except Exception as e:
            logger.error(f"Failed to fetch metadata for DOI {doi}: {e}")
            return {
                "doi": doi,
                "success": False,
                "error": str(e)
            }
    
    def is_valid_url(self, url: str) -> bool:
        """Check if URL is valid.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
