"""Document segmentation tool - no side effects."""
from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class Segmentation:
    """Tool for segmenting documents into logical sections."""
    
    def __init__(self):
        """Initialize segmentation tool."""
        self.section_patterns = [
            r'^#{1,3}\s+(.+)$',  # Markdown headers
            r'^\d+\.?\s+([A-Z][^.]+)$',  # Numbered sections
            r'^([A-Z][A-Z\s]+)$',  # All caps headings
        ]
    
    def segment(self, text: str, method: str = "auto") -> List[Dict[str, Any]]:
        """Segment text into logical sections.
        
        Args:
            text: Input text to segment
            method: Segmentation method ('auto', 'paragraph', 'sentence', 'heading')
            
        Returns:
            List of segments with metadata
        """
        if method == "auto":
            return self._segment_auto(text)
        elif method == "paragraph":
            return self._segment_by_paragraph(text)
        elif method == "sentence":
            return self._segment_by_sentence(text)
        elif method == "heading":
            return self._segment_by_heading(text)
        else:
            raise ValueError(f"Unknown segmentation method: {method}")
    
    def _segment_auto(self, text: str) -> List[Dict[str, Any]]:
        """Automatically detect best segmentation method."""
        # Try heading-based first
        heading_segments = self._segment_by_heading(text)
        
        if len(heading_segments) > 1:
            return heading_segments
        
        # Fall back to paragraph-based
        return self._segment_by_paragraph(text)
    
    def _segment_by_paragraph(self, text: str) -> List[Dict[str, Any]]:
        """Segment by paragraphs."""
        paragraphs = re.split(r'\n\s*\n', text)
        segments = []
        
        for i, para in enumerate(paragraphs):
            para = para.strip()
            if para:
                segments.append({
                    'segment_id': f'para_{i}',
                    'type': 'paragraph',
                    'content': para,
                    'position': i,
                    'length': len(para)
                })
        
        return segments
    
    def _segment_by_sentence(self, text: str) -> List[Dict[str, Any]]:
        """Segment by sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+\s+', text)
        segments = []
        
        for i, sent in enumerate(sentences):
            sent = sent.strip()
            if sent:
                segments.append({
                    'segment_id': f'sent_{i}',
                    'type': 'sentence',
                    'content': sent,
                    'position': i,
                    'length': len(sent)
                })
        
        return segments
    
    def _segment_by_heading(self, text: str) -> List[Dict[str, Any]]:
        """Segment by section headings."""
        lines = text.split('\n')
        segments = []
        current_section = None
        current_content = []
        section_level = 0
        
        for line in lines:
            # Check if line is a heading
            is_heading = False
            heading_text = None
            level = 0
            
            for pattern in self.section_patterns:
                match = re.match(pattern, line.strip())
                if match:
                    is_heading = True
                    heading_text = match.group(1) if match.groups() else line.strip()
                    # Detect level from markdown headers
                    if line.strip().startswith('#'):
                        level = len(line.strip()) - len(line.strip().lstrip('#'))
                    else:
                        level = 1
                    break
            
            if is_heading:
                # Save previous section
                if current_section is not None:
                    segments.append({
                        'segment_id': f'section_{len(segments)}',
                        'type': 'section',
                        'heading': current_section,
                        'level': section_level,
                        'content': '\n'.join(current_content).strip(),
                        'position': len(segments),
                        'length': sum(len(c) for c in current_content)
                    })
                
                # Start new section
                current_section = heading_text
                section_level = level
                current_content = []
            else:
                if line.strip():
                    current_content.append(line)
        
        # Add last section
        if current_section is not None:
            segments.append({
                'segment_id': f'section_{len(segments)}',
                'type': 'section',
                'heading': current_section,
                'level': section_level,
                'content': '\n'.join(current_content).strip(),
                'position': len(segments),
                'length': sum(len(c) for c in current_content)
            })
        
        return segments
    
    def merge_segments(
        self,
        segments: List[Dict[str, Any]],
        max_length: int = 1000
    ) -> List[Dict[str, Any]]:
        """Merge small segments to reach target length.
        
        Args:
            segments: List of segments to merge
            max_length: Maximum length per merged segment
            
        Returns:
            List of merged segments
        """
        merged = []
        current_group = []
        current_length = 0
        
        for segment in segments:
            seg_length = segment['length']
            
            if current_length + seg_length > max_length and current_group:
                # Save current group
                merged.append(self._create_merged_segment(current_group))
                current_group = [segment]
                current_length = seg_length
            else:
                current_group.append(segment)
                current_length += seg_length
        
        # Add remaining group
        if current_group:
            merged.append(self._create_merged_segment(current_group))
        
        return merged
    
    def _create_merged_segment(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a merged segment from multiple segments."""
        content = '\n\n'.join(s['content'] for s in segments)
        
        return {
            'segment_id': f"merged_{segments[0]['segment_id']}_{segments[-1]['segment_id']}",
            'type': 'merged',
            'content': content,
            'source_segments': [s['segment_id'] for s in segments],
            'position': segments[0]['position'],
            'length': len(content)
        }
