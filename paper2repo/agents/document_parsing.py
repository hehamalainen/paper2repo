"""Document Parsing Agent for paper ingestion and segmentation."""
from typing import Dict, Any
import logging
from pathlib import Path
from paper2repo.tools.perception.pdf_ingest import PDFIngest
from paper2repo.tools.cognitive.segmentation import Segmentation
from paper2repo.tools.cognitive.semantic_index import SemanticIndex

logger = logging.getLogger(__name__)


class DocumentParsingAgent:
    """Agent for parsing and indexing research documents."""
    
    def __init__(self):
        """Initialize document parsing agent."""
        self.pdf_ingest = PDFIngest()
        self.segmentation = Segmentation()
        self.semantic_index = SemanticIndex()
        self.agent_name = "document_parsing"
    
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and parse document.
        
        Args:
            input_data: Input containing document path or URL
            
        Returns:
            Document index
        """
        doc_path = input_data.get('document_path')
        doc_text = input_data.get('document_text')
        
        if doc_path:
            # Ingest PDF
            doc_path = Path(doc_path)
            if doc_path.suffix.lower() == '.pdf':
                content = self.pdf_ingest.ingest(doc_path)
                # Extract text from pages
                doc_text = '\n\n'.join(
                    page['text'] for page in content.get('pages', [])
                )
            else:
                # Read as text file
                doc_text = doc_path.read_text()
        
        if not doc_text:
            return {'error': 'No document content provided'}
        
        # Segment document
        segments = self.segmentation.segment(doc_text, method='auto')
        
        # Index segments
        document_id = input_data.get('document_id', 'doc_001')
        index_result = self.semantic_index.index_document(document_id, segments)
        
        logger.info(f"Parsed document with {len(segments)} segments")
        
        return {
            'document_id': document_id,
            'title': input_data.get('title', 'Untitled'),
            'sections': segments,
            'metadata': {
                'num_segments': len(segments),
                'source': str(doc_path) if doc_path else 'text_input'
            },
            'semantic_index': index_result
        }
