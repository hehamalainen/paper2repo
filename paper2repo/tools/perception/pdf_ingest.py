"""PDF document ingestion tool - no side effects."""
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class PDFIngest:
    """Tool for ingesting PDF documents."""
    
    def __init__(self):
        """Initialize PDF ingest tool."""
        self._pymupdf_available = False
        try:
            import fitz  # PyMuPDF
            self._pymupdf_available = True
        except ImportError:
            logger.warning("PyMuPDF not available. PDF ingestion will use fallback mode.")
    
    def ingest(self, pdf_path: Path) -> Dict[str, Any]:
        """Ingest PDF document and extract structured content.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted content
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if self._pymupdf_available:
            return self._ingest_with_pymupdf(pdf_path)
        else:
            return self._ingest_fallback(pdf_path)
    
    def _ingest_with_pymupdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Ingest PDF using PyMuPDF."""
        import fitz
        
        doc = fitz.open(str(pdf_path))
        pages = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            
            pages.append({
                "page_number": page_num + 1,
                "text": text,
                "metadata": {
                    "width": page.rect.width,
                    "height": page.rect.height
                }
            })
        
        metadata = doc.metadata
        doc.close()
        
        return {
            "file_path": str(pdf_path),
            "num_pages": len(pages),
            "pages": pages,
            "metadata": {
                "title": metadata.get("title", ""),
                "author": metadata.get("author", ""),
                "subject": metadata.get("subject", ""),
                "creator": metadata.get("creator", ""),
            }
        }
    
    def _ingest_fallback(self, pdf_path: Path) -> Dict[str, Any]:
        """Fallback ingestion when PyMuPDF not available."""
        return {
            "file_path": str(pdf_path),
            "num_pages": 0,
            "pages": [],
            "metadata": {},
            "error": "PyMuPDF not installed. Install with: pip install pymupdf"
        }
    
    def extract_sections(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract sections from PDF content.
        
        Args:
            content: Ingested PDF content
            
        Returns:
            List of extracted sections
        """
        sections = []
        
        # Simple section extraction based on page boundaries
        for page in content.get("pages", []):
            text = page["text"]
            
            # Basic section detection (can be enhanced)
            if text.strip():
                sections.append({
                    "page": page["page_number"],
                    "content": text,
                    "type": "page_section"
                })
        
        return sections
