"""
Hugging Face Spaces entry point for Paper2Repo.
Redirects to the main Streamlit app.
"""
import subprocess
import sys

if __name__ == "__main__":
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "paper2repo/ui/streamlit_app.py",
            "--server.port=7860",
            "--server.address=0.0.0.0"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error launching Streamlit app: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
