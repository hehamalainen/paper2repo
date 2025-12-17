"""Web user interface for Paper2Repo using Streamlit - MVP with BYOK."""
import sys
import os
import io
import tempfile
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any, List

# Check if streamlit is available
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

if not STREAMLIT_AVAILABLE:
    print("Error: Streamlit is not installed.")
    print("Install with: pip install -r requirements-streamlit.txt")
    sys.exit(1)

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from paper2repo import __version__


def validate_api_key(api_key: str) -> tuple[bool, Optional[str]]:
    """Validate OpenAI API key with a simple API call.
    
    Args:
        api_key: OpenAI API key to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not OPENAI_AVAILABLE:
        return False, "OpenAI library not installed"
    
    if not api_key or not api_key.startswith('sk-'):
        return False, "Invalid API key format"
    
    try:
        client = OpenAI(api_key=api_key)
        # Simple validation call - list models
        client.models.list()
        return True, None
    except openai.AuthenticationError:
        return False, "Invalid API key"
    except openai.RateLimitError:
        return False, "Rate limit exceeded"
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def extract_text_from_pdf(pdf_file) -> tuple[Optional[str], Optional[str]]:
    """Extract text from uploaded PDF file.
    
    Args:
        pdf_file: Uploaded PDF file from Streamlit
        
    Returns:
        Tuple of (extracted_text, error_message)
    """
    if not PYMUPDF_AVAILABLE:
        return None, "PyMuPDF not installed. Install with: pip install pymupdf"
    
    try:
        # Read PDF bytes
        pdf_bytes = pdf_file.read()
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        # Extract text from all pages
        text_parts = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text_parts.append(page.get_text())
        
        pdf_document.close()
        
        full_text = "\n\n".join(text_parts)
        
        if not full_text.strip():
            return None, "No text could be extracted from PDF"
        
        return full_text, None
    
    except Exception as e:
        return None, f"PDF parsing error: {str(e)}"


def generate_code_mock(api_key: str, paper_text: str, instructions: str, 
                       model: str, progress_callback=None) -> Dict[str, Any]:
    """Mock code generation for MVP.
    
    Args:
        api_key: OpenAI API key
        paper_text: Extracted paper text
        instructions: User instructions
        model: Model to use
        progress_callback: Callback for progress updates
        
    Returns:
        Dictionary with generation results
    """
    # Simulate phases
    phases = [
        "Phase 1: Analyzing paper structure...",
        "Phase 2: Extracting key concepts...",
        "Phase 3: Identifying algorithms...",
        "Phase 4: Planning code structure...",
        "Phase 5: Generating code files...",
        "Phase 6: Creating documentation..."
    ]
    
    for i, phase in enumerate(phases):
        if progress_callback:
            progress_callback(phase, (i + 1) / len(phases))
    
    # Mock generated files
    generated_files = {
        "README.md": f"""# Generated Code from Paper

## Overview
This code was generated from the research paper using Paper2Repo.

## Instructions
{instructions if instructions else 'No additional instructions provided'}

## Files
- `main.py`: Main implementation
- `utils.py`: Utility functions
- `tests/test_main.py`: Unit tests
- `requirements.txt`: Dependencies

## Usage
```bash
pip install -r requirements.txt
python main.py
```
""",
        "main.py": """\"\"\"Main implementation generated from paper.\"\"\"

def main():
    \"\"\"Main function.\"\"\"
    print("Hello from generated code!")
    # TODO: Implement paper algorithms here
    
if __name__ == "__main__":
    main()
""",
        "utils.py": """\"\"\"Utility functions.\"\"\"

def helper_function(x):
    \"\"\"Helper function.\"\"\"
    return x * 2
""",
        "tests/test_main.py": """\"\"\"Unit tests for main module.\"\"\"
import pytest
from main import main

def test_main():
    \"\"\"Test main function.\"\"\"
    main()  # Should not raise
""",
        "requirements.txt": """pytest>=7.4.0
numpy>=1.24.0
"""
    }
    
    return {
        'success': True,
        'files': generated_files,
        'stats': {
            'total_files': len(generated_files),
            'lines_of_code': sum(len(content.split('\n')) for content in generated_files.values()),
            'model_used': model
        }
    }


def create_zip_file(files: Dict[str, str]) -> bytes:
    """Create a ZIP file from generated files.
    
    Args:
        files: Dictionary mapping file paths to content
        
    Returns:
        ZIP file bytes
    """
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path, content in files.items():
            zip_file.writestr(file_path, content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()


def display_file_tree(files: Dict[str, str]) -> None:
    """Display file tree structure.
    
    Args:
        files: Dictionary mapping file paths to content
    """
    st.markdown("### 📁 Generated Files")
    
    # Organize files by directory
    tree = {}
    for file_path in sorted(files.keys()):
        parts = file_path.split('/')
        current = tree
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = None
    
    def render_tree(node, prefix="", is_last=True):
        """Recursively render tree structure."""
        items = sorted(node.items())
        for i, (name, children) in enumerate(items):
            is_last_item = (i == len(items) - 1)
            connector = "└── " if is_last_item else "├── "
            
            if children is None:
                # File
                st.text(f"{prefix}{connector}📄 {name}")
            else:
                # Directory
                st.text(f"{prefix}{connector}📁 {name}/")
                extension = "    " if is_last_item else "│   "
                render_tree(children, prefix + extension, is_last_item)
    
    render_tree(tree)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Paper2Repo - Transform Papers to Code",
        page_icon="📄➡️💻",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'api_key_validated' not in st.session_state:
        st.session_state.api_key_validated = False
    if 'generated_files' not in st.session_state:
        st.session_state.generated_files = None
    
    # Sidebar - API Key Configuration
    with st.sidebar:
        st.header("🔑 Configuration")
        
        # API Key Input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Your API key is never stored and only used for this session",
            placeholder="sk-..."
        )
        
        # Validate API key when provided
        if api_key:
            if st.session_state.get('last_api_key') != api_key:
                with st.spinner("Validating API key..."):
                    is_valid, error_msg = validate_api_key(api_key)
                    st.session_state.api_key_validated = is_valid
                    st.session_state.last_api_key = api_key
                    if not is_valid:
                        st.session_state.api_key_error = error_msg
            
            # Show validation status
            if st.session_state.api_key_validated:
                st.success("✅ API Key Valid")
            else:
                st.error(f"❌ {st.session_state.get('api_key_error', 'Invalid API Key')}")
                st.markdown("""
                [Get your OpenAI API key](https://platform.openai.com/api-keys)
                """)
        else:
            st.info("👆 Enter your OpenAI API key to get started")
            st.markdown("""
            [Get your OpenAI API key](https://platform.openai.com/api-keys)
            """)
        
        st.divider()
        
        # Model Selection (optional)
        if st.session_state.api_key_validated:
            model = st.selectbox(
                "Model",
                options=["gpt-4o", "gpt-4o-mini"],
                index=1,  # Default to gpt-4o-mini
                help="Select the model for code generation"
            )
        else:
            model = "gpt-4o-mini"
        
        st.divider()
        
        # Security Notice
        st.caption("🔒 Your API key is never stored and only used for this session")
    
    # Main Area
    st.title("Paper2Repo 📄➡️💻")
    st.markdown("**Transform research papers into working code**")
    
    st.divider()
    
    # PDF Upload
    uploaded_file = st.file_uploader(
        "📄 Upload Research Paper (PDF)",
        type=['pdf'],
        help="Upload a PDF of the research paper you want to convert to code"
    )
    
    # Optional Instructions
    instructions = st.text_area(
        "💡 Additional Instructions (Optional)",
        placeholder="e.g., 'Include unit tests', 'Use NumPy for calculations', 'Add detailed comments'",
        help="Provide any specific requirements or preferences for the generated code"
    )
    
    # Generate Button
    can_generate = (
        st.session_state.api_key_validated 
        and uploaded_file is not None
    )
    
    generate_button = st.button(
        "🚀 Generate Code",
        type="primary",
        disabled=not can_generate,
        use_container_width=True
    )
    
    if not can_generate and uploaded_file:
        st.warning("⚠️ Please enter a valid API key to generate code")
    
    # Generation Process
    if generate_button:
        # Extract text from PDF
        with st.spinner("📖 Extracting text from PDF..."):
            paper_text, error = extract_text_from_pdf(uploaded_file)
        
        if error:
            st.error(f"❌ {error}")
            st.info("💡 Make sure the PDF contains selectable text (not just images)")
        else:
            # Show progress
            progress_bar = st.progress(0.0)
            status_text = st.empty()
            
            def update_progress(message: str, progress: float):
                status_text.text(message)
                progress_bar.progress(progress)
            
            # Generate code
            try:
                results = generate_code_mock(
                    api_key,
                    paper_text,
                    instructions,
                    model,
                    update_progress
                )
                
                # Store results in session state
                st.session_state.generated_files = results['files']
                st.session_state.generation_stats = results['stats']
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                st.success("✅ Code generated successfully!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Generation error: {str(e)}")
                st.info("💡 Try again or check your API key")
    
    # Results Display
    if st.session_state.generated_files:
        st.divider()
        st.header("📦 Generated Code")
        
        # Stats
        stats = st.session_state.generation_stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Files Generated", stats['total_files'])
        with col2:
            st.metric("Lines of Code", stats['lines_of_code'])
        with col3:
            st.metric("Model Used", stats['model_used'])
        
        # File Tree
        display_file_tree(st.session_state.generated_files)
        
        st.divider()
        
        # Code Preview with Tabs
        st.markdown("### 👀 Code Preview")
        file_tabs = st.tabs([Path(f).name for f in sorted(st.session_state.generated_files.keys())])
        
        for tab, (file_path, content) in zip(file_tabs, sorted(st.session_state.generated_files.items())):
            with tab:
                # Determine language for syntax highlighting
                ext = Path(file_path).suffix
                language_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.md': 'markdown',
                    '.txt': 'text',
                    '.json': 'json',
                    '.yaml': 'yaml',
                    '.yml': 'yaml'
                }
                language = language_map.get(ext, 'text')
                
                st.code(content, language=language, line_numbers=True)
        
        st.divider()
        
        # Download ZIP
        st.markdown("### 💾 Download Code")
        zip_bytes = create_zip_file(st.session_state.generated_files)
        
        st.download_button(
            label="⬇️ Download as ZIP",
            data=zip_bytes,
            file_name="paper2repo_generated_code.zip",
            mime="application/zip",
            use_container_width=True
        )


if __name__ == '__main__':
    main()
