"""GitHub repository search tool - no side effects."""
from typing import Dict, Any, List, Optional
import logging
import requests
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class GitHubSearch:
    """Tool for searching GitHub repositories."""
    
    def __init__(self, api_token: Optional[str] = None):
        """Initialize GitHub search tool.
        
        Args:
            api_token: Optional GitHub API token for higher rate limits
        """
        self.api_token = api_token
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Paper2Repo/1.0'
        }
        
        if api_token:
            headers['Authorization'] = f'token {api_token}'
        
        self.session.headers.update(headers)
    
    def search_repositories(
        self,
        query: str,
        language: Optional[str] = None,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 10
    ) -> Dict[str, Any]:
        """Search GitHub repositories.
        
        Args:
            query: Search query
            language: Filter by programming language
            sort: Sort by 'stars', 'forks', or 'updated'
            order: Order 'asc' or 'desc'
            per_page: Results per page (max 100)
            
        Returns:
            Search results
        """
        # Build search query
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        params = {
            'q': search_query,
            'sort': sort,
            'order': order,
            'per_page': min(per_page, 100)
        }
        
        url = f"{self.base_url}/search/repositories"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            items = []
            for repo in data.get('items', []):
                items.append({
                    'name': repo['name'],
                    'full_name': repo['full_name'],
                    'description': repo.get('description', ''),
                    'url': repo['html_url'],
                    'stars': repo['stargazers_count'],
                    'forks': repo['forks_count'],
                    'language': repo.get('language', ''),
                    'topics': repo.get('topics', []),
                    'updated_at': repo['updated_at']
                })
            
            return {
                'total_count': data['total_count'],
                'items': items,
                'success': True
            }
        except Exception as e:
            logger.error(f"GitHub search failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_repository_info(self, owner: str, repo: str) -> Dict[str, Any]:
        """Get detailed repository information.
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Repository information
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            return {
                'name': data['name'],
                'full_name': data['full_name'],
                'description': data.get('description', ''),
                'url': data['html_url'],
                'clone_url': data['clone_url'],
                'stars': data['stargazers_count'],
                'forks': data['forks_count'],
                'language': data.get('language', ''),
                'topics': data.get('topics', []),
                'license': data.get('license', {}).get('name', ''),
                'created_at': data['created_at'],
                'updated_at': data['updated_at'],
                'readme_url': f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md",
                'success': True
            }
        except Exception as e:
            logger.error(f"Failed to get repository info: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search_code(
        self,
        query: str,
        language: Optional[str] = None,
        per_page: int = 10
    ) -> Dict[str, Any]:
        """Search code on GitHub.
        
        Args:
            query: Search query
            language: Filter by programming language
            per_page: Results per page
            
        Returns:
            Search results
        """
        search_query = query
        if language:
            search_query += f" language:{language}"
        
        params = {
            'q': search_query,
            'per_page': min(per_page, 100)
        }
        
        url = f"{self.base_url}/search/code"
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            items = []
            for item in data.get('items', []):
                items.append({
                    'name': item['name'],
                    'path': item['path'],
                    'repository': item['repository']['full_name'],
                    'url': item['html_url'],
                })
            
            return {
                'total_count': data['total_count'],
                'items': items,
                'success': True
            }
        except Exception as e:
            logger.error(f"Code search failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
