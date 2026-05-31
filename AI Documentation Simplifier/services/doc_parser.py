"""
services/doc_parser.py — Fetches a documentation URL and extracts clean text content.
"""

import requests
from bs4 import BeautifulSoup
import sys
sys.path.append("..")
from config import MAX_DOC_LENGTH


def fetch_documentation(url: str) -> str:
    """
    Fetch a documentation page and extract the main text content.
    Works well with AWS docs, blog posts, and most technical pages.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove noise elements
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
        tag.decompose()

    # Try to find the main content area
    main_content = (
        soup.find("main") or
        soup.find("article") or
        soup.find("div", {"id": "main-content"}) or
        soup.find("div", {"id": "main-col-body"}) or  # AWS docs specific
        soup.find("div", {"role": "main"}) or
        soup.body
    )

    if main_content is None:
        main_content = soup

    # Extract text
    text = main_content.get_text(separator="\n", strip=True)

    # Clean up
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    clean_text = "\n".join(lines)

    # Truncate if needed
    if len(clean_text) > MAX_DOC_LENGTH:
        clean_text = clean_text[:MAX_DOC_LENGTH] + "\n\n[... content truncated for processing ...]"

    return clean_text
