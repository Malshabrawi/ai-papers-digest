"""
Fetch viral AI papers from arXiv and Hugging Face with impact scoring
Rotates through top-tier conferences daily for diverse high-quality sources
"""
import os
import requests
import arxiv
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

# Top-tier conferences and venues for AI/ML research
TOP_TIER_VENUES = {
    'neurips': {'name': 'NeurIPS', 'bonus': 50, 'focus': 'ML foundations, RL, agents'},
    'icml': {'name': 'ICML', 'bonus': 50, 'focus': 'Core ML theory'},
    'iclr': {'name': 'ICLR', 'bonus': 50, 'focus': 'Deep learning'},
    'aamas': {'name': 'AAMAS', 'bonus': 60, 'focus': 'Autonomous agents (most relevant!)'},
    'aaai': {'name': 'AAAI', 'bonus': 45, 'focus': 'Broad AI'},
    'ijcai': {'name': 'IJCAI', 'bonus': 45, 'focus': 'Broad AI'},
    'cvpr': {'name': 'CVPR', 'bonus': 40, 'focus': 'Computer vision'},
    'acl': {'name': 'ACL', 'bonus': 40, 'focus': 'NLP/Language agents'},
    'emnlp': {'name': 'EMNLP', 'bonus': 40, 'focus': 'NLP'},
    'corl': {'name': 'CoRL', 'bonus': 45, 'focus': 'Robot learning'},
}

# arXiv categories for different focuses
ARXIV_CATEGORIES = [
    'cs.AI',  # Artificial Intelligence
    'cs.MA',  # Multiagent Systems (key for agentic AI!)
    'cs.LG',  # Machine Learning
    'cs.RO',  # Robotics
    'cs.CL',  # Computation and Language
]


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


def get_daily_arxiv_category() -> str:
    """Get arXiv category for today (rotates daily)"""
    day_of_year = datetime.now().timetuple().tm_yday
    category_index = day_of_year % len(ARXIV_CATEGORIES)
    return ARXIV_CATEGORIES[category_index]


def detect_paper_venue(paper: Dict) -> Optional[str]:
    """Detect if paper is from a top-tier conference based on title/abstract"""
    searchable_text = (
        paper.get('title', '').lower() + ' ' +
        paper.get('abstract', '').lower()
    )

    # Check for conference mentions in paper metadata
    for venue_key, venue_info in TOP_TIER_VENUES.items():
        venue_name = venue_info['name'].lower()
        if venue_name in searchable_text:
            return venue_key

    return None


def fetch_arxiv_papers(topic: str = "", num_papers: int = 5, category: str = None) -> List[Dict]:
    """Fetch recent papers from arXiv based on topic and category"""
    try:
        # Use provided category or get daily rotation
        arxiv_category = category if category else get_daily_arxiv_category()

        # Build search query
        if topic:
            search_query = f'all:"{topic}" AND cat:{arxiv_category}'
        else:
            search_query = f'cat:{arxiv_category}'

        print(f"  Searching arXiv category: {arxiv_category}")

        # Search arXiv
        search = arxiv.Search(
            query=search_query,
            max_results=num_papers * 2,  # Fetch more for better filtering
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers = []
        for result in search.results():
            paper = {
                'title': result.title,
                'authors': ', '.join([author.name for author in result.authors]),
                'abstract': result.summary,
                'arxiv_id': result.entry_id.split('/')[-1],
                'pdf_url': result.pdf_url,
                'published_date': result.published.isoformat(),
                'upvotes': 0,
                'source': f'arXiv ({arxiv_category})',
                'arxiv_category': arxiv_category
            }

            # Detect if from top-tier venue
            venue = detect_paper_venue(paper)
            if venue:
                paper['venue'] = venue
                paper['source'] = f"{TOP_TIER_VENUES[venue]['name']} (arXiv)"

            papers.append(paper)

        return papers[:num_papers]
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
    - Venue bonus: +40-60 points for top-tier conferences
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

    # Venue bonus (top-tier conferences get priority)
    venue = paper.get('venue')
    if venue and venue in TOP_TIER_VENUES:
        venue_bonus = TOP_TIER_VENUES[venue]['bonus']
        score += venue_bonus
        paper['venue_bonus'] = venue_bonus  # Track for display

    return score


def fetch_high_impact_papers(topic: str = None, num_papers: int = 5) -> List[Dict]:
    """
    Fetch high-impact papers using hybrid approach:
    1. Get Hugging Face trending papers (community validated)
    2. Add arXiv papers from daily-rotating category
    3. Filter by topic if specified
    4. Enrich with Semantic Scholar citation data
    5. Detect top-tier venues and add bonus
    6. Sort by impact score
    """
    # Show daily rotation info
    daily_category = get_daily_arxiv_category()
    print("=" * 80)
    print(f"📚 Daily Source Rotation:")
    print(f"  Today's arXiv category: {daily_category}")
    print(f"  Bonus for top-tier venues: NeurIPS, ICML, ICLR, AAMAS, etc.")
    print("=" * 80)

    print("\nFetching papers with impact scoring...")

    # Get more papers than needed for better filtering
    fetch_count = num_papers * 3 if topic else num_papers

    # Fetch from Hugging Face (already curated for quality)
    print("1. Fetching trending papers from Hugging Face...")
    hf_papers = fetch_huggingface_papers(fetch_count)

    # Always add arXiv papers from daily rotation
    print(f"2. Fetching from arXiv (rotating category)...")
    arxiv_papers = fetch_arxiv_papers(topic if topic else "", num_papers * 2, daily_category)

    # Combine sources
    all_papers = hf_papers + arxiv_papers

    # Filter by topic if specified
    if topic:
        print(f"3. Filtering papers by topic: '{topic}'")
        filtered_papers = filter_papers_by_topic(all_papers, topic)
        print(f"   Found {len(filtered_papers)} papers matching topic")
    else:
        filtered_papers = all_papers

    # Enrich with citation data from Semantic Scholar
    print("4. Enriching with citation data...")
    for paper in filtered_papers[:20]:  # Limit API calls
        arxiv_id = paper.get('arxiv_id', '')
        if arxiv_id:
            scholar_data = get_semantic_scholar_data(arxiv_id)
            paper['citations'] = scholar_data['citations']
            paper['influential_citations'] = scholar_data['influential_citations']
            time.sleep(0.1)  # Rate limiting

    # Detect venues for all papers
    print("5. Detecting top-tier conference venues...")
    venue_count = 0
    for paper in filtered_papers:
        if not paper.get('venue'):  # Only if not already detected
            venue = detect_paper_venue(paper)
            if venue:
                paper['venue'] = venue
                venue_count += 1
    if venue_count > 0:
        print(f"   Found {venue_count} papers from top-tier venues!")

    # Calculate impact scores
    print("6. Calculating impact scores...")
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

    print(f"\n✅ Selected {len(result)} highest-impact papers:")
    for i, paper in enumerate(result, 1):
        venue_tag = f" [{TOP_TIER_VENUES[paper['venue']]['name']}]" if paper.get('venue') else ""
        print(f"  {i}. {paper['title'][:55]}...{venue_tag}")
        print(f"     Score: {paper['impact_score']:.0f} | Citations: {paper.get('citations', 0)} | Source: {paper.get('source', 'Unknown')}")

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
