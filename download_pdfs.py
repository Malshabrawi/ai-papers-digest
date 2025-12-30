"""
Download PDF papers to local folder
"""
import os
import requests
from datetime import datetime
from typing import List, Dict
from pathlib import Path


def create_papers_folder(base_folder: str = "papers") -> str:
    """
    Create a folder for today's papers

    Args:
        base_folder: Base folder name for papers

    Returns:
        Path to today's papers folder
    """
    today = datetime.now().strftime('%Y-%m-%d')
    folder_path = os.path.join(base_folder, today)

    Path(folder_path).mkdir(parents=True, exist_ok=True)
    print(f"📁 Created folder: {folder_path}")

    return folder_path


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Limit length
    if len(filename) > 200:
        filename = filename[:200]

    return filename


def download_pdf(paper: Dict, folder_path: str, index: int) -> str:
    """
    Download a single PDF paper

    Args:
        paper: Paper dictionary with pdf_url
        folder_path: Folder to save the PDF
        index: Paper number for filename

    Returns:
        Path to downloaded PDF or empty string if failed
    """
    try:
        pdf_url = paper['pdf_url']
        arxiv_id = paper.get('arxiv_id', f'paper_{index}')

        # Create filename from paper title
        title = paper['title']
        sanitized_title = sanitize_filename(title)
        filename = f"{index:02d}_{arxiv_id}_{sanitized_title[:100]}.pdf"
        file_path = os.path.join(folder_path, filename)

        # Download PDF
        print(f"📥 Downloading: {title[:60]}...")
        response = requests.get(pdf_url, timeout=30, stream=True)
        response.raise_for_status()

        # Save to file
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = os.path.getsize(file_path) / 1024  # KB
        print(f"   ✅ Saved: {filename} ({file_size:.1f} KB)")

        return file_path

    except Exception as e:
        print(f"   ❌ Error downloading {paper['title'][:50]}...: {e}")
        return ""


def download_all_papers(papers: List[Dict], base_folder: str = "papers") -> Dict[str, any]:
    """
    Download all papers to a dated folder

    Args:
        papers: List of paper dictionaries
        base_folder: Base folder for papers

    Returns:
        Dictionary with folder_path and list of downloaded files
    """
    folder_path = create_papers_folder(base_folder)

    downloaded_files = []
    failed_downloads = []

    for i, paper in enumerate(papers, 1):
        file_path = download_pdf(paper, folder_path, i)

        if file_path:
            downloaded_files.append(file_path)
        else:
            failed_downloads.append(paper['title'])

    print(f"\n📊 Download Summary:")
    print(f"   ✅ Success: {len(downloaded_files)}/{len(papers)}")
    if failed_downloads:
        print(f"   ❌ Failed: {len(failed_downloads)}")
        for title in failed_downloads:
            print(f"      - {title[:60]}")

    return {
        'folder_path': folder_path,
        'downloaded_files': downloaded_files,
        'failed_downloads': failed_downloads
    }


def create_index_file(papers: List[Dict], folder_path: str):
    """
    Create an index.txt file listing all papers

    Args:
        papers: List of paper dictionaries
        folder_path: Folder containing the papers
    """
    index_path = os.path.join(folder_path, 'INDEX.txt')

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(f"AI Papers - {datetime.now().strftime('%Y-%m-%d')}\n")
        f.write("=" * 80 + "\n\n")

        for i, paper in enumerate(papers, 1):
            f.write(f"{i}. {paper['title']}\n")
            f.write(f"   Authors: {paper['authors']}\n")
            f.write(f"   arXiv ID: {paper['arxiv_id']}\n")
            f.write(f"   PDF: {paper['pdf_url']}\n")
            f.write(f"   Published: {paper['published_date']}\n")
            f.write(f"   Source: {paper['source']}\n")
            if paper.get('summary'):
                f.write(f"\n   Summary:\n")
                for line in paper['summary'].split('\n'):
                    f.write(f"   {line}\n")
            f.write("\n" + "-" * 80 + "\n\n")

    print(f"📝 Created index file: {index_path}")


if __name__ == "__main__":
    # Test downloader
    test_papers = [{
        'title': 'Attention Is All You Need',
        'authors': 'Vaswani et al.',
        'arxiv_id': '1706.03762',
        'pdf_url': 'https://arxiv.org/pdf/1706.03762.pdf',
        'published_date': '2017-06-12',
        'source': 'arXiv',
        'summary': 'Test summary'
    }]

    print("Testing PDF downloader...")
    result = download_all_papers(test_papers, base_folder="test_papers")
    print(f"\nDownloaded to: {result['folder_path']}")
