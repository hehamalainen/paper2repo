"""Retrieval tool for finding relevant information - no side effects."""
from typing import Dict, Any, List, Optional, Tuple
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class Retrieval:
    """Tool for retrieving relevant information from indexed content."""
    
    def __init__(self, semantic_index=None):
        """Initialize retrieval tool.
        
        Args:
            semantic_index: Optional semantic index instance
        """
        self.semantic_index = semantic_index
        self.retrieval_gate_threshold = 0.3  # Minimum relevance score
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant content for query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional filters (document_id, type, etc.)
            
        Returns:
            List of retrieved content with metadata
        """
        if self.semantic_index is None:
            logger.warning("No semantic index available for retrieval")
            return []
        
        # Get document filter
        document_id = filters.get('document_id') if filters else None
        
        # Perform semantic search
        results = self.semantic_index.search(
            query=query,
            top_k=top_k * 2,  # Get more candidates for filtering
            document_id=document_id
        )
        
        # Apply retrieval gate
        filtered_results = self._apply_retrieval_gate(results, query)
        
        # Apply additional filters
        if filters:
            filtered_results = self._apply_filters(filtered_results, filters)
        
        # Limit to top_k
        return filtered_results[:top_k]
    
    def _apply_retrieval_gate(
        self,
        results: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """Apply retrieval gate to filter low-quality results.
        
        Args:
            results: Raw retrieval results
            query: Original query
            
        Returns:
            Filtered results
        """
        filtered = []
        
        for result in results:
            score = result['score']
            
            # Check if score meets threshold
            if score >= self.retrieval_gate_threshold:
                # Add gate metadata
                result['gate_passed'] = True
                result['gate_score'] = score
                filtered.append(result)
            else:
                logger.debug(
                    f"Result filtered by gate: score={score:.3f} < "
                    f"threshold={self.retrieval_gate_threshold}"
                )
        
        return filtered
    
    def _apply_filters(
        self,
        results: List[Dict[str, Any]],
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Apply additional filters to results.
        
        Args:
            results: Results to filter
            filters: Filter criteria
            
        Returns:
            Filtered results
        """
        filtered = results
        
        # Filter by type
        if 'type' in filters:
            type_filter = filters['type']
            filtered = [
                r for r in filtered
                if r['segment'].get('type') == type_filter
            ]
        
        # Filter by minimum length
        if 'min_length' in filters:
            min_length = filters['min_length']
            filtered = [
                r for r in filtered
                if len(r['segment'].get('content', '')) >= min_length
            ]
        
        return filtered
    
    def retrieve_with_context(
        self,
        query: str,
        context_window: int = 1,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve content with surrounding context.
        
        Args:
            query: Search query
            context_window: Number of neighboring segments to include
            top_k: Number of primary results
            
        Returns:
            Results with context
        """
        # Get primary results
        primary_results = self.retrieve(query, top_k=top_k)
        
        # Expand with context
        expanded_results = []
        
        for result in primary_results:
            segment = result['segment']
            segment_id = segment['segment_id']
            
            # Get related segments (context)
            if self.semantic_index:
                context_segments = self.semantic_index.get_related_segments(
                    segment_id,
                    top_k=context_window * 2
                )
            else:
                context_segments = []
            
            expanded_results.append({
                'primary_segment': segment,
                'primary_score': result['score'],
                'context_segments': context_segments[:context_window]
            })
        
        return expanded_results
    
    def extract_relationships(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Tuple[str, str, str]]:
        """Extract relationship tuples from retrieval results.
        
        Args:
            results: Retrieval results
            
        Returns:
            List of (subject, predicate, object) tuples
        """
        relationships = []
        
        for result in results:
            segment = result['segment']
            content = segment.get('content', '')
            
            # Simple relationship extraction (can be enhanced with NLP)
            # Look for common patterns like "X is Y", "X uses Y", etc.
            patterns = [
                ('is', r'(\w+)\s+is\s+(\w+)'),
                ('uses', r'(\w+)\s+uses?\s+(\w+)'),
                ('depends_on', r'(\w+)\s+depends?\s+on\s+(\w+)'),
            ]
            
            import re
            for predicate, pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    if len(match) == 2:
                        relationships.append((match[0], predicate, match[1]))
        
        return relationships
    
    def rank_by_relevance(
        self,
        results: List[Dict[str, Any]],
        relevance_criteria: Optional[Dict[str, float]] = None
    ) -> List[Dict[str, Any]]:
        """Re-rank results by custom relevance criteria.
        
        Args:
            results: Results to rank
            relevance_criteria: Weights for different criteria
            
        Returns:
            Re-ranked results
        """
        if not relevance_criteria:
            relevance_criteria = {
                'semantic_score': 0.6,
                'recency': 0.2,
                'length': 0.2
            }
        
        for result in results:
            scores = {
                'semantic_score': result.get('score', 0.0),
                'recency': 1.0 - result['segment'].get('metadata', {}).get('position', 0) / 100.0,
                'length': min(len(result['segment'].get('content', '')) / 1000.0, 1.0)
            }
            
            # Compute weighted score
            weighted_score = sum(
                scores.get(criterion, 0.0) * weight
                for criterion, weight in relevance_criteria.items()
            )
            
            result['relevance_score'] = weighted_score
        
        # Sort by relevance score
        results.sort(key=lambda x: x.get('relevance_score', 0.0), reverse=True)
        
        return results
