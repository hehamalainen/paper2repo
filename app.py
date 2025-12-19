"""
Hugging Face Spaces entry point for Paper2Repo.
Direct import of Streamlit app for HF Spaces compatibility.
"""
# Import and run the main Streamlit app directly
# HF Spaces with sdk:streamlit handles the Streamlit server
from paper2repo.ui.streamlit_app import main

if __name__ == "__main__":
    main()
