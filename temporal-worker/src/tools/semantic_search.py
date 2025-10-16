"""
Semantic search tools for finding related papers and calculating similarity.
Uses NLP techniques for intelligent paper relationship discovery.
"""

import re
from typing import Any, Dict, List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


async def find_similar_papers(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Find papers similar to a reference paper using semantic search.
    
    Args:
        args: Dictionary containing:
            - reference_paper: Paper text or abstract for comparison
            - search_corpus: List of papers to search through
            - max_results: Maximum similar papers to return
            - similarity_threshold: Minimum similarity score
            
    Returns:
        List of similar papers with similarity scores
    """
    
    reference_paper = args.get("reference_paper", "")
    search_corpus = args.get("search_corpus", [])
    max_results = args.get("max_results", 10)
    similarity_threshold = args.get("similarity_threshold", 0.1)
    
    if not reference_paper:
        return {
            "success": False,
            "error": "Reference paper text is required",
            "similar_papers": []
        }
    
    if not search_corpus:
        # Use sample corpus if none provided
        search_corpus = _get_sample_corpus()
    
    try:
        # Preprocess texts
        reference_text = _preprocess_text(reference_paper)
        corpus_texts = [_preprocess_text(paper.get("text", "")) for paper in search_corpus]
        
        # Create combined corpus for vectorization
        all_texts = [reference_text] + corpus_texts
        
        # Vectorize using TF-IDF
        vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        
        # Calculate similarities
        reference_vector = tfidf_matrix[0:1]
        corpus_vectors = tfidf_matrix[1:]
        
        similarities = cosine_similarity(reference_vector, corpus_vectors).flatten()
        
        # Create results with similarity scores
        similar_papers = []
        for idx, similarity_score in enumerate(similarities):
            if similarity_score >= similarity_threshold:
                paper = search_corpus[idx].copy()
                paper["similarity_score"] = float(similarity_score)
                paper["similarity_rank"] = len(similar_papers) + 1
                similar_papers.append(paper)
        
        # Sort by similarity score
        similar_papers.sort(key=lambda x: x["similarity_score"], reverse=True)
        
        # Limit results
        similar_papers = similar_papers[:max_results]
        
        return {
            "success": True,
            "similar_papers": similar_papers,
            "search_metadata": {
                "reference_text_length": len(reference_text),
                "corpus_size": len(search_corpus),
                "similarity_threshold": similarity_threshold,
                "max_results": max_results,
                "results_found": len(similar_papers)
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Similarity search failed: {str(e)}",
            "similar_papers": []
        }


async def calculate_paper_similarity(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate semantic similarity between two papers.
    
    Args:
        args: Dictionary containing:
            - paper1_text: Text content of first paper
            - paper2_text: Text content of second paper
            - method: Similarity calculation method
            
    Returns:
        Similarity score and detailed comparison metrics
    """
    
    paper1_text = args.get("paper1_text", "")
    paper2_text = args.get("paper2_text", "")
    method = args.get("method", "tfidf_cosine")
    
    if not paper1_text or not paper2_text:
        return {
            "success": False,
            "error": "Both paper texts are required",
            "similarity": {}
        }
    
    try:
        # Preprocess texts
        text1 = _preprocess_text(paper1_text)
        text2 = _preprocess_text(paper2_text)
        
        # Calculate similarity based on method
        if method == "tfidf_cosine":
            similarity_data = _calculate_tfidf_similarity(text1, text2)
        elif method == "jaccard":
            similarity_data = _calculate_jaccard_similarity(text1, text2)
        elif method == "word_overlap":
            similarity_data = _calculate_word_overlap(text1, text2)
        else:
            # Default to TF-IDF cosine
            similarity_data = _calculate_tfidf_similarity(text1, text2)
        
        # Add metadata
        similarity_data["comparison_metadata"] = {
            "paper1_length": len(text1),
            "paper2_length": len(text2),
            "method": method,
            "paper1_words": len(text1.split()),
            "paper2_words": len(text2.split())
        }
        
        return {
            "success": True,
            "similarity": similarity_data
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Similarity calculation failed: {str(e)}",
            "similarity": {}
        }


def _preprocess_text(text: str) -> str:
    """Preprocess text for similarity analysis."""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common academic paper artifacts
    text = re.sub(r'\b(?:fig|figure|table|equation|eq)\s*\d+\b', '', text)
    text = re.sub(r'\b(?:section|sec)\s*\d+\b', '', text)
    
    return text.strip()


def _calculate_tfidf_similarity(text1: str, text2: str) -> Dict[str, Any]:
    """Calculate TF-IDF cosine similarity between two texts."""
    
    # Vectorize texts
    vectorizer = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1, 2),
        max_features=1000
    )
    
    tfidf_matrix = vectorizer.fit_transform([text1, text2])
    
    # Calculate cosine similarity
    similarity_matrix = cosine_similarity(tfidf_matrix)
    similarity_score = similarity_matrix[0, 1]
    
    # Get feature names for analysis
    feature_names = vectorizer.get_feature_names_out()
    
    # Find top common terms
    tfidf1 = tfidf_matrix[0].toarray().flatten()
    tfidf2 = tfidf_matrix[1].toarray().flatten()
    
    # Get top terms for each document
    top_terms1 = [(feature_names[i], tfidf1[i]) for i in tfidf1.argsort()[-10:][::-1] if tfidf1[i] > 0]
    top_terms2 = [(feature_names[i], tfidf2[i]) for i in tfidf2.argsort()[-10:][::-1] if tfidf2[i] > 0]
    
    # Find common important terms
    common_terms = []
    for term1, score1 in top_terms1:
        for term2, score2 in top_terms2:
            if term1 == term2:
                common_terms.append({
                    "term": term1,
                    "score1": score1,
                    "score2": score2,
                    "avg_score": (score1 + score2) / 2
                })
    
    return {
        "method": "tfidf_cosine",
        "similarity_score": float(similarity_score),
        "top_terms_paper1": top_terms1[:5],
        "top_terms_paper2": top_terms2[:5],
        "common_important_terms": sorted(common_terms, key=lambda x: x["avg_score"], reverse=True)[:5]
    }


def _calculate_jaccard_similarity(text1: str, text2: str) -> Dict[str, Any]:
    """Calculate Jaccard similarity between word sets."""
    
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    jaccard_score = len(intersection) / len(union) if union else 0
    
    return {
        "method": "jaccard",
        "similarity_score": jaccard_score,
        "common_words": len(intersection),
        "total_unique_words": len(union),
        "words_paper1": len(words1),
        "words_paper2": len(words2),
        "sample_common_words": list(intersection)[:10]
    }


def _calculate_word_overlap(text1: str, text2: str) -> Dict[str, Any]:
    """Calculate word overlap similarity."""
    
    words1 = text1.split()
    words2 = text2.split()
    
    # Count word frequencies
    freq1 = {}
    freq2 = {}
    
    for word in words1:
        freq1[word] = freq1.get(word, 0) + 1
    
    for word in words2:
        freq2[word] = freq2.get(word, 0) + 1
    
    # Calculate overlap
    common_words = set(freq1.keys()).intersection(set(freq2.keys()))
    overlap_count = sum(min(freq1[word], freq2[word]) for word in common_words)
    
    total_words = len(words1) + len(words2)
    overlap_ratio = (2 * overlap_count) / total_words if total_words > 0 else 0
    
    return {
        "method": "word_overlap",
        "similarity_score": overlap_ratio,
        "overlap_count": overlap_count,
        "common_unique_words": len(common_words),
        "total_words": total_words,
        "overlap_percentage": overlap_ratio * 100
    }


def _get_sample_corpus() -> List[Dict[str, Any]]:
    """Get sample corpus for testing when no corpus provided."""
    
    return [
        {
            "id": "sample_1",
            "title": "Machine Learning in Healthcare",
            "text": "Machine learning algorithms are increasingly being applied to healthcare data to improve patient outcomes and reduce costs."
        },
        {
            "id": "sample_2", 
            "title": "Deep Learning for Natural Language Processing",
            "text": "Deep neural networks have revolutionized natural language processing tasks including translation, summarization, and sentiment analysis."
        },
        {
            "id": "sample_3",
            "title": "Computer Vision Applications",
            "text": "Computer vision techniques using convolutional neural networks enable automated image analysis and object recognition."
        }
    ]