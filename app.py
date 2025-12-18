"""
Hugging Face Spaces entry point for Paper2Repo.
Redirects to the main Streamlit app.
"""
import subprocess
import sys

if __name__ == "__main__":
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        "paper2repo/ui/streamlit_app.py",
        "--server.port=7860",
        "--server.address=0.0.0.0"
    ])
