"""
Summarize papers using Google Gemini AI
"""
import os
import google.generativeai as genai
from typing import Dict, List


def initialize_gemini(api_key: str):
    """Initialize Gemini AI with API key"""
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('models/gemini-2.5-flash')


def summarize_paper(model, paper: Dict) -> str:
    """
    Summarize a single paper using Gemini AI

    Args:
        model: Gemini model instance
        paper: Paper dictionary with title and abstract

    Returns:
        AI-generated summary string
    """
    prompt = f"""Summarize this AI research paper and extract key findings:

Title: {paper['title']}

Abstract: {paper['abstract']}

Please provide:
1. Main Contribution (2-3 sentences)
2. Key Findings (3-5 bullet points)
3. Potential Impact (1-2 sentences)

Keep the summary under 200 words and make it accessible to someone with general AI knowledge."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error summarizing paper '{paper['title'][:50]}...': {e}")
        return f"Error generating summary: {str(e)}"


def summarize_papers(papers: List[Dict], api_key: str) -> List[Dict]:
    """
    Summarize multiple papers using Gemini AI

    Args:
        papers: List of paper dictionaries
        api_key: Gemini API key

    Returns:
        List of papers with added 'summary' field
    """
    print(f"Initializing Gemini AI for summarization...")
    model = initialize_gemini(api_key)

    summarized_papers = []

    for i, paper in enumerate(papers, 1):
        print(f"Summarizing paper {i}/{len(papers)}: {paper['title'][:60]}...")
        summary = summarize_paper(model, paper)

        paper_with_summary = paper.copy()
        paper_with_summary['summary'] = summary
        summarized_papers.append(paper_with_summary)

    print(f"Successfully summarized {len(summarized_papers)} papers")
    return summarized_papers


if __name__ == "__main__":
    # Test the summarizer
    from dotenv import load_dotenv
    load_dotenv()

    test_paper = {
        'title': 'Attention Is All You Need',
        'abstract': 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...'
    }

    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        model = initialize_gemini(api_key)
        summary = summarize_paper(model, test_paper)
        print("\nTest Summary:")
        print(summary)
    else:
        print("GEMINI_API_KEY not found in .env file")
