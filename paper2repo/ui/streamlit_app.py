"""Web user interface for Paper2Repo using Streamlit."""
import sys
from pathlib import Path

# Check if streamlit is available
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

if not STREAMLIT_AVAILABLE:
    print("Error: Streamlit is not installed.")
    print("Install with: pip install 'paper2repo[ui]'")
    sys.exit(1)

from paper2repo import __version__
from paper2repo.workflows.pipeline_orchestrator import PipelineOrchestrator


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Paper2Repo",
        page_icon="📄",
        layout="wide"
    )
    
    st.title(f"📄 Paper2Repo v{__version__}")
    st.markdown("Transform research papers into production-ready code repositories")
    
    # Sidebar configuration
    st.sidebar.header("Configuration")
    
    output_dir = st.sidebar.text_input(
        "Output Directory",
        value="./output"
    )
    
    token_budget = st.sidebar.number_input(
        "Token Budget",
        min_value=100000,
        max_value=10000000,
        value=1000000,
        step=100000
    )
    
    # Main interface
    tab1, tab2, tab3 = st.tabs(["Generate", "Results", "About"])
    
    with tab1:
        st.header("Generate Code from Paper")
        
        # Input method selection
        input_method = st.radio(
            "Input Method",
            ["Upload PDF", "Paste Text", "File Path"]
        )
        
        document_path = None
        document_text = None
        user_input = None
        
        if input_method == "Upload PDF":
            uploaded_file = st.file_uploader(
                "Upload Research Paper (PDF)",
                type=['pdf']
            )
            if uploaded_file:
                # Save uploaded file
                temp_path = Path(f"/tmp/{uploaded_file.name}")
                temp_path.write_bytes(uploaded_file.read())
                document_path = str(temp_path)
        
        elif input_method == "Paste Text":
            document_text = st.text_area(
                "Paper Content",
                height=300,
                placeholder="Paste the research paper content here..."
            )
        
        elif input_method == "File Path":
            document_path = st.text_input(
                "Paper File Path",
                placeholder="/path/to/paper.pdf"
            )
        
        user_input = st.text_input(
            "Additional Requirements (optional)",
            placeholder="e.g., 'Implement in Python with tests'"
        )
        
        if st.button("🚀 Generate Code", type="primary"):
            if not document_path and not document_text:
                st.error("Please provide a paper (file or text)")
            else:
                with st.spinner("Generating code... This may take several minutes."):
                    try:
                        # Initialize pipeline
                        pipeline = PipelineOrchestrator(
                            output_dir=Path(output_dir),
                            total_token_budget=token_budget
                        )
                        
                        # Prepare input
                        input_data = {
                            'user_input': user_input or "Generate code from paper"
                        }
                        
                        if document_path:
                            input_data['document_path'] = document_path
                        if document_text:
                            input_data['document_text'] = document_text
                        
                        # Run pipeline
                        results = pipeline.run(input_data)
                        
                        # Store results in session state
                        st.session_state['results'] = results
                        st.session_state['output_dir'] = str(pipeline.get_output_directory())
                        
                        if results['success']:
                            st.success("✅ Code generated successfully!")
                            st.info(f"📁 Output: {pipeline.get_output_directory()}")
                        else:
                            st.error("❌ Generation failed")
                            for error in results.get('errors', []):
                                st.error(f"Error: {error}")
                    
                    except Exception as e:
                        st.error(f"Pipeline error: {e}")
    
    with tab2:
        st.header("Generation Results")
        
        if 'results' in st.session_state:
            results = st.session_state['results']
            
            # Show success status
            if results['success']:
                st.success("✅ Generation successful")
            else:
                st.error("❌ Generation failed")
            
            # Show token usage
            if 'token_budget' in results:
                budget = results['token_budget']
                st.metric(
                    "Token Usage",
                    f"{budget['used_tokens']:,}",
                    f"{budget['utilization']:.1%} of budget"
                )
            
            # Show phases
            st.subheader("Pipeline Phases")
            for phase_name, phase_data in results.get('phases', {}).items():
                with st.expander(f"📋 {phase_name}"):
                    st.json(phase_data.get('artifacts', {}))
            
            # Show generated files
            if 'artifacts' in results and 'code_files' in results['artifacts']:
                st.subheader("Generated Files")
                files = results['artifacts']['code_files'].get('generated_files', [])
                for file_info in files:
                    st.text(f"✓ {file_info['path']} ({file_info['size']} bytes)")
        else:
            st.info("No results yet. Generate code in the 'Generate' tab.")
    
    with tab3:
        st.header("About Paper2Repo")
        st.markdown(f"""
        **Version:** {__version__}
        
        **Paper2Repo** is an AI-powered multi-agent platform that transforms 
        research papers into production-ready code repositories.
        
        ### Features
        - 📄 PDF and text input support
        - 🤖 Multi-agent architecture
        - 🔍 Concept and algorithm extraction
        - 💻 Code generation with verification
        - 📊 Token budget management
        
        ### Pipeline Phases
        1. **P1 Blueprint**: Intent understanding, document parsing, concept/algorithm analysis
        2. **P2 CodeGen**: Reference mining, code generation
        3. **P3 Verify**: Validation and refinement
        
        ### Documentation
        Visit [GitHub](https://github.com/hehamalainen/paper2repo) for full documentation.
        """)


if __name__ == '__main__':
    main()
