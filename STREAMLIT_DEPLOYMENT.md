# Streamlit Cloud Deployment Guide

## Overview
This guide explains how to deploy the Paper2Repo MVP Streamlit app to Streamlit Cloud.

## Prerequisites
- GitHub account
- Streamlit Cloud account (free tier available at https://streamlit.io/cloud)
- This repository pushed to GitHub

## Deployment Steps

### 1. Connect to Streamlit Cloud
1. Visit https://streamlit.io/cloud
2. Sign in with your GitHub account
3. Click "New app"

### 2. Configure the App
- **Repository**: hehamalainen/paper2repo
- **Branch**: copilot/simplify-streamlit-ui (or main after merge)
- **Main file path**: `paper2repo/ui/streamlit_app.py`

### 3. Advanced Settings (Optional)
- **Python version**: 3.11 or higher
- **Requirements file**: `requirements-streamlit.txt`

### 4. Deploy
Click "Deploy!" and wait for the app to build and launch.

## Configuration Files

### `.streamlit/config.toml`
Pre-configured with:
- Custom theme (indigo primary color)
- 25MB upload limit
- Clean UI styling

### `requirements-streamlit.txt`
Minimal dependencies for fast deployment:
- streamlit>=1.28.0
- openai>=1.0.0
- tiktoken>=0.5.0
- pymupdf>=1.23.0
- pyyaml>=6.0
- pydantic>=2.0.0
- requests>=2.28.0
- python-dotenv>=1.0.0
- jinja2>=3.1.0
- numpy>=1.24.0

## Features

### User Experience
1. **API Key Input**: Users enter their own OpenAI API key
2. **Key Validation**: Real-time validation with clear status
3. **PDF Upload**: Drag-and-drop or browse for PDF files (up to 25MB)
4. **Code Generation**: Mock generation with progress tracking
5. **Results Display**: File tree, code preview, and ZIP download

### Security
- API keys never stored or logged
- Only session-based storage
- Keys hashed for comparison
- Password field for key input
- Clear security notices

## Testing Locally

To test the app locally before deploying:

```bash
# Install dependencies
pip install -r requirements-streamlit.txt

# Install paper2repo
pip install -e .

# Run the app
streamlit run paper2repo/ui/streamlit_app.py
```

The app will open in your browser at http://localhost:8501

## User Instructions

When users access the app:
1. Enter OpenAI API key in sidebar (get from https://platform.openai.com/api-keys)
2. Wait for validation (✅ or ❌)
3. Upload a PDF research paper
4. Optionally add instructions (e.g., "Include unit tests")
5. Click "Generate Code"
6. View results and download ZIP

## Troubleshooting

### "Streamlit not installed"
Ensure `requirements-streamlit.txt` is being used during deployment.

### "OpenAI library not installed"
Check that openai>=1.0.0 is in requirements-streamlit.txt.

### PDF parsing errors
Ensure PyMuPDF (fitz) is installed and PDF contains selectable text.

### API key validation fails
- Check internet connectivity
- Verify API key format (starts with 'sk-')
- Check OpenAI account has valid credits
- May be rate limited - wait and retry

## Future Enhancements

- Integration with actual Paper2Repo pipeline
- Support for more file formats
- Enhanced code preview with editing
- Direct GitHub repository creation
- Batch processing of multiple papers
