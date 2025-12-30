"""
Fetch viral AI papers from arXiv and Hugging Face with impact scoring
"""
import os
import requests
import arxiv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


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


def get_semantic_scholar_data(arxiv_id: str) -> Dict:
    """Fetch citation data from Semantic Scholar API"""
    try:
        # Clean arxiv ID
        clean_id = arxiv_id.replace('arXiv:', '').replace('v1', '').replace('v2', '').replace('v3', '')

        url = f"https://api.semanticscholar.org/graph/v1/paper/arXiv:{clean_id}"
        params = {
            'fields': 'citationCount,influentialCitationCount,publicationDate,title'
        }

        response = requests.get(url, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            return {
                'citations': data.get('citationCount', 0),
                'influential_citations': data.get('influentialCitationCount', 0)
            }
    except Exception as e:
        print(f"Could not fetch Semantic Scholar data for {arxiv_id}: {e}")

    return {'citations': 0, 'influential_citations': 0}


def filter_papers_by_topic(papers: List[Dict], topic: str) -> List[Dict]:
    """Filter papers by topic keywords"""
    if not topic:
        return papers

    topic_keywords = topic.lower().split()
    filtered = []

    for paper in papers:
        # Search in title and abstract
        searchable_text = (
            paper.get('title', '').lower() + ' ' +
            paper.get('abstract', '').lower()
        )

        # Check if any keyword matches
        if any(keyword in searchable_text for keyword in topic_keywords):
            filtered.append(paper)

    return filtered


def calculate_impact_score(paper: Dict, topic: str = None) -> float:
    """
    Calculate impact score for a paper

    Score formula:
    - Upvotes (HF): 2 points each
    - Citations: 5 points each
    - Influential citations: 10 points each
    - Recency bonus: +20 points if published in last 30 days
    - Topic relevance: +30 points if keywords in title
    """
    score = 0.0

    # Upvotes from Hugging Face
    score += paper.get('upvotes', 0) * 2

    # Citations from Semantic Scholar
    score += paper.get('citations', 0) * 5
    score += paper.get('influential_citations', 0) * 10

    # Recency bonus
    try:
        pub_date = datetime.fromisoformat(paper.get('published_date', '').replace('Z', '+00:00'))
        days_old = (datetime.now(pub_date.tzinfo) - pub_date).days
        if days_old <= 30:
            score += 20
        elif days_old <= 90:
            score += 10
    except:
        pass

    # Topic relevance (keywords in title get bonus)
    if topic:
        title = paper.get('title', '').lower()
        keywords = topic.lower().split()
        if any(keyword in title for keyword in keywords):
            score += 30

    return score


def fetch_high_impact_papers(topic: str = None, num_papers: int = 5) -> List[Dict]:
    """
    Fetch high-impact papers using hybrid approach:
    1. Get Hugging Face trending papers (community validated)
    2. Filter by topic if specified
    3. Enrich with Semantic Scholar citation data
    4. Sort by impact score
    """
    print("Fetching papers with impact scoring...")

    # Get more papers than needed for better filtering
    fetch_count = num_papers * 3 if topic else num_papers

    # Fetch from Hugging Face (already curated for quality)
    print("Fetching trending papers from Hugging Face...")
    hf_papers = fetch_huggingface_papers(fetch_count)

    # Filter by topic if specified
    if topic:
        print(f"Filtering papers by topic: {topic}")
        filtered_papers = filter_papers_by_topic(hf_papers, topic)

        # If not enough papers after filtering, add from arXiv
        if len(filtered_papers) < num_papers:
            print(f"Found {len(filtered_papers)} matching papers, searching arXiv...")
            arxiv_papers = fetch_arxiv_papers(topic, num_papers * 2)
            filtered_papers.extend(arxiv_papers)
    else:
        filtered_papers = hf_papers

    # Enrich with citation data from Semantic Scholar
    print("Enriching with citation data...")
    for paper in filtered_papers[:20]:  # Limit API calls
        arxiv_id = paper.get('arxiv_id', '')
        if arxiv_id:
            scholar_data = get_semantic_scholar_data(arxiv_id)
            paper['citations'] = scholar_data['citations']
            paper['influential_citations'] = scholar_data['influential_citations']
            time.sleep(0.1)  # Rate limiting

    # Calculate impact scores
    for paper in filtered_papers:
        paper['impact_score'] = calculate_impact_score(paper, topic)

    # Sort by impact score (highest first)
    sorted_papers = sorted(
        filtered_papers,
        key=lambda p: p['impact_score'],
        reverse=True
    )

    # Return top N papers
    result = sorted_papers[:num_papers]

    print(f"Selected {len(result)} high-impact papers")
    for i, paper in enumerate(result, 1):
        print(f"  {i}. {paper['title'][:60]}... (score: {paper['impact_score']:.0f}, citations: {paper.get('citations', 0)})")

    return result


def get_papers(topic: Optional[str] = None, num_papers: int = 5) -> List[Dict]:
    """
    Get high-impact AI papers using hybrid approach

    Args:
        topic: Optional topic filter (e.g., "agentic ai", "large language models")
        num_papers: Number of papers to fetch

    Returns:
        List of paper dictionaries sorted by impact score
    """
    # Use the new high-impact selection method
    papers = fetch_high_impact_papers(topic, num_papers)

    # Fallback to old method if new one fails
    if not papers:
        print("Falling back to standard fetching method...")
        if not topic or topic.strip() == "":
            papers = fetch_huggingface_papers(num_papers)
        else:
            papers = fetch_arxiv_papers(topic, num_papers)

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
