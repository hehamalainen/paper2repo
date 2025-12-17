"""Semantic indexing tool - no side effects."""
from typing import Dict, Any, List, Optional
import logging
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class SemanticIndex:
    """Tool for creating semantic indexes of document content."""
    
    def __init__(self, embedding_dim: int = 384):
        """Initialize semantic index.
        
        Args:
            embedding_dim: Dimension of embeddings
        """
        self.embedding_dim = embedding_dim
        self.index: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, np.ndarray] = {}
    
    def index_document(
        self,
        document_id: str,
        segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Index document segments.
        
        Args:
            document_id: Unique document identifier
            segments: List of document segments
            
        Returns:
            Index metadata
        """
        indexed_segments = []
        
        for segment in segments:
            segment_id = f"{document_id}_{segment.get('segment_id', len(indexed_segments))}"
            
            # Generate mock embedding (in real implementation, use sentence transformers)
            embedding = self._generate_embedding(segment['content'])
            
            self.embeddings[segment_id] = embedding
            
            indexed_segment = {
                'segment_id': segment_id,
                'document_id': document_id,
                'content': segment['content'],
                'type': segment.get('type', 'unknown'),
                'metadata': {
                    'length': len(segment['content']),
                    'position': segment.get('position', 0)
                }
            }
            
            indexed_segments.append(indexed_segment)
            self.index[segment_id] = indexed_segment
        
        return {
            'document_id': document_id,
            'num_segments': len(indexed_segments),
            'indexed_segments': indexed_segments
        }
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for text (mock implementation).
        
        Args:
            text: Input text
            
        Returns:
            Embedding vector
        """
        # Mock embedding based on text hash for consistency
        np.random.seed(hash(text) % (2**32))
        embedding = np.random.randn(self.embedding_dim)
        # Normalize
        embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        return embedding
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search index for relevant segments.
        
        Args:
            query: Search query
            top_k: Number of results to return
            document_id: Optional filter by document ID
            
        Returns:
            List of matching segments with scores
        """
        query_embedding = self._generate_embedding(query)
        
        # Filter segments
        candidates = self.index.values()
        if document_id:
            candidates = [s for s in candidates if s['document_id'] == document_id]
        
        # Compute similarities
        results = []
        for segment in candidates:
            segment_id = segment['segment_id']
            embedding = self.embeddings.get(segment_id)
            
            if embedding is not None:
                similarity = np.dot(query_embedding, embedding)
                results.append({
                    'segment': segment,
                    'score': float(similarity)
                })
        
        # Sort by similarity
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
    
    def get_segment(self, segment_id: str) -> Optional[Dict[str, Any]]:
        """Get segment by ID.
        
        Args:
            segment_id: Segment identifier
            
        Returns:
            Segment data or None
        """
        return self.index.get(segment_id)
    
    def get_related_segments(
        self,
        segment_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Find segments related to given segment.
        
        Args:
            segment_id: Reference segment ID
            top_k: Number of results to return
            
        Returns:
            List of related segments with scores
        """
        segment = self.get_segment(segment_id)
        if not segment:
            return []
        
        return self.search(segment['content'], top_k=top_k + 1)[1:]  # Exclude self
    
    def cluster_segments(
        self,
        num_clusters: int = 5
    ) -> Dict[int, List[str]]:
        """Cluster indexed segments.
        
        Args:
            num_clusters: Number of clusters
            
        Returns:
            Mapping from cluster ID to segment IDs
        """
        if not self.embeddings:
            return {}
        
        # Simple k-means clustering (mock implementation)
        segment_ids = list(self.embeddings.keys())
        embeddings = np.array([self.embeddings[sid] for sid in segment_ids])
        
        # Random cluster assignment for now
        np.random.seed(42)
        cluster_assignments = np.random.randint(0, num_clusters, size=len(segment_ids))
        
        clusters = defaultdict(list)
        for segment_id, cluster_id in zip(segment_ids, cluster_assignments):
            clusters[int(cluster_id)].append(segment_id)
        
        return dict(clusters)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics.
        
        Returns:
            Statistics dictionary
        """
        document_ids = set(s['document_id'] for s in self.index.values())
        
        return {
            'num_documents': len(document_ids),
            'num_segments': len(self.index),
            'embedding_dim': self.embedding_dim
        }
