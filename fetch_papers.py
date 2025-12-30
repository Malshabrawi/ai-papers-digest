"""
Fetch viral AI papers from arXiv and Hugging Face
"""
import os
import requests
import arxiv
from datetime import datetime, timedelta
from typing import List, Dict, Optional


def fetch_huggingface_papers(num_papers: int = 5) -> List[Dict]:
    """Fetch trending papers from Hugging Face daily papers"""
    try:
        url = "https://huggingface.co/api/daily_papers"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        papers_data = response.json()
        papers = []

        for paper in papers_data[:num_papers]:
            paper_info = paper.get('paper', {})
            papers.append({
                'title': paper_info.get('title', 'Untitled'),
                'authors': ', '.join([a.get('name', '') for a in paper_info.get('authors', [])]),
                'abstract': paper_info.get('summary', 'No abstract available'),
                'arxiv_id': paper_info.get('id', ''),
                'pdf_url': f"https://arxiv.org/pdf/{paper_info.get('id', '')}.pdf",
                'published_date': paper.get('publishedAt', datetime.now().isoformat()),
                'upvotes': paper.get('upvotes', 0),
                'source': 'Hugging Face Daily'
            })

        return papers
    except Exception as e:
        print(f"Error fetching from Hugging Face: {e}")
        return []


def fetch_arxiv_papers(topic: str = "", num_papers: int = 5) -> List[Dict]:
    """Fetch recent papers from arXiv based on topic"""
    try:
        # Build search query
        if topic:
            search_query = f'all:"{topic}" AND cat:cs.AI'
        else:
            search_query = 'cat:cs.AI OR cat:cs.LG OR cat:cs.CL'

        # Search arXiv
        search = arxiv.Search(
            query=search_query,
            max_results=num_papers,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers = []
        for result in search.results():
            papers.append({
                'title': result.title,
                'authors': ', '.join([author.name for author in result.authors]),
                'abstract': result.summary,
                'arxiv_id': result.entry_id.split('/')[-1],
                'pdf_url': result.pdf_url,
                'published_date': result.published.isoformat(),
                'upvotes': 0,
                'source': 'arXiv'
            })

        return papers
    except Exception as e:
        print(f"Error fetching from arXiv: {e}")
        return []


def get_papers(topic: Optional[str] = None, num_papers: int = 5) -> List[Dict]:
    """
    Get viral AI papers from multiple sources

    Args:
        topic: Optional topic filter (e.g., "agentic ai", "large language models")
        num_papers: Number of papers to fetch

    Returns:
        List of paper dictionaries
    """
    papers = []

    # If no topic specified, get from Hugging Face daily papers
    if not topic or topic.strip() == "":
        print("Fetching trending papers from Hugging Face...")
        papers = fetch_huggingface_papers(num_papers)
    else:
        # If topic specified, search arXiv
        print(f"Searching arXiv for papers about: {topic}")
        papers = fetch_arxiv_papers(topic, num_papers)

        # If not enough papers found, supplement with HF daily papers
        if len(papers) < num_papers:
            print(f"Found {len(papers)} papers, supplementing with trending papers...")
            hf_papers = fetch_huggingface_papers(num_papers - len(papers))
            papers.extend(hf_papers)

    print(f"Successfully fetched {len(papers)} papers")
    return papers


if __name__ == "__main__":
    # Test the fetcher
    print("Testing paper fetcher...")
    test_papers = get_papers(num_papers=3)

    for i, paper in enumerate(test_papers, 1):
        print(f"\n{i}. {paper['title']}")
        print(f"   Authors: {paper['authors'][:100]}...")
        print(f"   Source: {paper['source']}")
