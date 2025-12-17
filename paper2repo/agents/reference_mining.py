"""Reference Mining Agent for repository discovery and indexing."""
from typing import Dict, Any
import logging
from paper2repo.tools.perception.github_search import GitHubSearch
from paper2repo.memory.coderag import CodeRAG

logger = logging.getLogger(__name__)


class ReferenceMiningAgent:
    """Agent for discovering and indexing external code references."""
    
    def __init__(self):
        """Initialize reference mining agent."""
        self.github_search = GitHubSearch()
        self.code_rag = CodeRAG()
        self.agent_name = "reference_mining"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mine and index external references.
        
        Args:
            input_data: Concepts and keywords to search
            
        Returns:
            Indexed references
        """
        concepts = input_data.get('concepts', {})
        
        # Extract keywords from concepts
        keywords = []
        if isinstance(concepts, dict) and 'concepts' in concepts:
            for concept in concepts.get('concepts', [])[:5]:  # Top 5 concepts
                if isinstance(concept, dict):
                    keywords.append(concept.get('name', ''))
        
        if not keywords:
            keywords = ['machine learning', 'algorithm']  # Default
        
        # Search GitHub for relevant repositories
        indexed_repos = []
        
        for keyword in keywords[:3]:  # Limit to 3 searches
            search_results = self.github_search.search_repositories(
                query=keyword,
                per_page=3
            )
            
            if search_results.get('success'):
                for repo in search_results.get('items', []):
                    # Index repository
                    self.code_rag.add_repository(
                        repo_id=repo['full_name'],
                        metadata=repo,
                        code_snippets=[]
                    )
                    indexed_repos.append(repo['full_name'])
        
        logger.info(f"Indexed {len(indexed_repos)} repositories")
        
        return {
            'indexed_repositories': indexed_repos,
            'code_rag_stats': self.code_rag.get_stats()
        }
