"""Code RAG system for external repository grounding with relationship tuples."""
from typing import Dict, Any, List, Optional, Tuple
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class RelationshipTuple:
    """Represents a relationship tuple (subject, predicate, object)."""
    
    def __init__(self, subject: str, predicate: str, obj: str, confidence: float = 1.0):
        """Initialize relationship tuple.
        
        Args:
            subject: Subject entity
            predicate: Relationship type
            obj: Object entity
            confidence: Confidence score (0-1)
        """
        self.subject = subject
        self.predicate = predicate
        self.object = obj
        self.confidence = confidence
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'subject': self.subject,
            'predicate': self.predicate,
            'object': self.object,
            'confidence': self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RelationshipTuple':
        """Create from dictionary."""
        return cls(
            subject=data['subject'],
            predicate=data['predicate'],
            obj=data['object'],
            confidence=data.get('confidence', 1.0)
        )


class CodeRAG:
    """Code RAG system for grounding with external repositories."""
    
    def __init__(self, retrieval_gate_threshold: float = 0.3):
        """Initialize Code RAG.
        
        Args:
            retrieval_gate_threshold: Minimum confidence for retrieval
        """
        self.retrieval_gate_threshold = retrieval_gate_threshold
        self.relationship_tuples: List[RelationshipTuple] = []
        self.repository_index: Dict[str, Dict[str, Any]] = {}
        self.concept_to_code: Dict[str, List[str]] = defaultdict(list)
    
    def add_relationship(self, tuple: RelationshipTuple) -> None:
        """Add a relationship tuple.
        
        Args:
            tuple: Relationship tuple to add
        """
        self.relationship_tuples.append(tuple)
        logger.debug(
            f"Added relationship: {tuple.subject} {tuple.predicate} {tuple.object}"
        )
    
    def add_repository(
        self,
        repo_id: str,
        metadata: Dict[str, Any],
        code_snippets: List[Dict[str, Any]]
    ) -> None:
        """Index an external repository.
        
        Args:
            repo_id: Repository identifier
            metadata: Repository metadata
            code_snippets: Code snippets from the repository
        """
        self.repository_index[repo_id] = {
            'metadata': metadata,
            'code_snippets': code_snippets
        }
        
        logger.info(f"Indexed repository: {repo_id}")
    
    def map_concept_to_code(self, concept_id: str, code_reference: str) -> None:
        """Map a concept to code implementation.
        
        Args:
            concept_id: Concept identifier from paper
            code_reference: Reference to code (repo_id:file:function)
        """
        self.concept_to_code[concept_id].append(code_reference)
        logger.debug(f"Mapped concept {concept_id} to {code_reference}")
    
    def retrieve_grounding(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Retrieve grounding information for query.
        
        Args:
            query: Query string
            top_k: Number of results to return
            
        Returns:
            List of grounding results
        """
        results = []
        
        # Search relationship tuples
        for tuple in self.relationship_tuples:
            # Simple string matching (can be enhanced with embeddings)
            query_lower = query.lower()
            
            if (query_lower in tuple.subject.lower() or
                query_lower in tuple.predicate.lower() or
                query_lower in tuple.object.lower()):
                
                # Apply retrieval gate
                if tuple.confidence >= self.retrieval_gate_threshold:
                    results.append({
                        'type': 'relationship',
                        'tuple': tuple.to_dict(),
                        'score': tuple.confidence
                    })
        
        # Search repository code snippets
        for repo_id, repo_data in self.repository_index.items():
            for snippet in repo_data['code_snippets']:
                if query.lower() in snippet.get('content', '').lower():
                    results.append({
                        'type': 'code_snippet',
                        'repo_id': repo_id,
                        'snippet': snippet,
                        'score': 0.8  # Fixed score for code matches
                    })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        
        return results[:top_k]
    
    def get_concept_implementations(self, concept_id: str) -> List[Dict[str, Any]]:
        """Get code implementations for a concept.
        
        Args:
            concept_id: Concept identifier
            
        Returns:
            List of code implementations
        """
        implementations = []
        
        for code_ref in self.concept_to_code.get(concept_id, []):
            # Parse code reference (repo_id:file:function)
            parts = code_ref.split(':')
            
            if len(parts) >= 1:
                repo_id = parts[0]
                
                if repo_id in self.repository_index:
                    implementations.append({
                        'code_reference': code_ref,
                        'repository': self.repository_index[repo_id]['metadata']
                    })
        
        return implementations
    
    def find_related_concepts(
        self,
        concept_id: str,
        max_depth: int = 2
    ) -> List[Tuple[str, str]]:
        """Find concepts related to given concept.
        
        Args:
            concept_id: Starting concept
            max_depth: Maximum relationship depth
            
        Returns:
            List of (related_concept, relationship_path) tuples
        """
        related = []
        visited = set()
        
        def traverse(current: str, path: str, depth: int):
            if depth > max_depth or current in visited:
                return
            
            visited.add(current)
            
            for tuple in self.relationship_tuples:
                if tuple.subject == current and tuple.confidence >= self.retrieval_gate_threshold:
                    new_path = f"{path} -> {tuple.predicate} -> {tuple.object}"
                    related.append((tuple.object, new_path))
                    traverse(tuple.object, new_path, depth + 1)
        
        traverse(concept_id, concept_id, 0)
        
        return related
    
    def extract_relationships_from_text(
        self,
        text: str,
        entity_types: Optional[List[str]] = None
    ) -> List[RelationshipTuple]:
        """Extract relationship tuples from text.
        
        Args:
            text: Input text
            entity_types: Optional filter for entity types
            
        Returns:
            List of extracted relationship tuples
        """
        # Simple pattern-based extraction (can be enhanced with NLP)
        import re
        
        extracted = []
        
        patterns = [
            (r'(\w+)\s+is\s+(?:a|an)\s+(\w+)', 'is_a'),
            (r'(\w+)\s+uses?\s+(\w+)', 'uses'),
            (r'(\w+)\s+implements?\s+(\w+)', 'implements'),
            (r'(\w+)\s+extends?\s+(\w+)', 'extends'),
            (r'(\w+)\s+depends?\s+on\s+(\w+)', 'depends_on'),
        ]
        
        for pattern, predicate in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    tuple = RelationshipTuple(
                        subject=match[0],
                        predicate=predicate,
                        obj=match[1],
                        confidence=0.7  # Pattern-based confidence
                    )
                    extracted.append(tuple)
        
        return extracted
    
    def apply_retrieval_gate(
        self,
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply retrieval gate to filter low-confidence results.
        
        Args:
            results: Results to filter
            
        Returns:
            Filtered results
        """
        filtered = []
        
        for result in results:
            score = result.get('score', 0.0)
            
            if score >= self.retrieval_gate_threshold:
                result['gate_passed'] = True
                filtered.append(result)
            else:
                logger.debug(
                    f"Result filtered by gate: score={score:.3f} < "
                    f"threshold={self.retrieval_gate_threshold}"
                )
        
        return filtered
    
    def get_stats(self) -> Dict[str, Any]:
        """Get Code RAG statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            'total_relationships': len(self.relationship_tuples),
            'total_repositories': len(self.repository_index),
            'total_concept_mappings': len(self.concept_to_code),
            'retrieval_gate_threshold': self.retrieval_gate_threshold,
            'avg_confidence': sum(t.confidence for t in self.relationship_tuples) / len(self.relationship_tuples) if self.relationship_tuples else 0
        }
