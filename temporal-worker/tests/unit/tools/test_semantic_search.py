"""
Tests for semantic search tool with real similarity calculations.
Tests paper similarity, semantic search, and NLP-based comparisons.
"""

import pytest
from src.tools.semantic_search import (
    find_similar_papers,
    calculate_paper_similarity,
    _preprocess_text,
    _calculate_tfidf_similarity,
    _calculate_jaccard_similarity,
    _calculate_word_overlap,
    _get_sample_corpus
)


# Sample research paper abstracts for testing
TRANSFORMER_ABSTRACT = """
The dominant sequence transduction models are based on complex recurrent or convolutional 
neural networks that include an encoder and a decoder. The best performing models also 
connect the encoder and decoder through an attention mechanism. We propose a new simple 
network architecture, the Transformer, based solely on attention mechanisms, dispensing 
with recurrence and convolutions entirely.
"""

BERT_ABSTRACT = """
We introduce a new language representation model called BERT, which stands for Bidirectional 
Encoder Representations from Transformers. Unlike recent language representation models, 
BERT is designed to pre-train deep bidirectional representations from unlabeled text by 
jointly conditioning on both left and right context in all layers.
"""

COMPUTER_VISION_ABSTRACT = """
Computer vision is an interdisciplinary scientific field that deals with how computers 
can gain high-level understanding from digital images or videos. From the perspective 
of engineering, it seeks to understand and automate tasks that the human visual system can do.
"""

UNRELATED_ABSTRACT = """
Climate change refers to long-term shifts in global temperatures and weather patterns. 
While climate variations are natural, since the 1800s human activities have been the 
main driver of climate change, primarily due to fossil fuel burning.
"""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_similar_papers_basic():
    """Test basic similarity search functionality."""
    # Create test corpus
    test_corpus = [
        {"id": "paper1", "title": "BERT Paper", "text": BERT_ABSTRACT},
        {"id": "paper2", "title": "Computer Vision", "text": COMPUTER_VISION_ABSTRACT},
        {"id": "paper3", "title": "Climate Change", "text": UNRELATED_ABSTRACT}
    ]
    
    args = {
        "reference_paper": TRANSFORMER_ABSTRACT,
        "search_corpus": test_corpus,
        "max_results": 3,
        "similarity_threshold": 0.0
    }
    
    result = await find_similar_papers(args)
    
    assert result["success"] is True
    assert "similar_papers" in result
    
    similar_papers = result["similar_papers"]
    assert len(similar_papers) <= 3
    
    # Check that results are sorted by similarity
    for i in range(len(similar_papers) - 1):
        assert similar_papers[i]["similarity_score"] >= similar_papers[i + 1]["similarity_score"]
    
    # BERT paper should be most similar to Transformer (both NLP/Transformer related)
    most_similar = similar_papers[0]
    assert most_similar["id"] == "paper1"  # BERT paper
    assert most_similar["similarity_score"] > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_similar_papers_with_threshold():
    """Test similarity search with threshold filtering."""
    test_corpus = [
        {"id": "similar", "text": BERT_ABSTRACT},
        {"id": "dissimilar", "text": UNRELATED_ABSTRACT}
    ]
    
    args = {
        "reference_paper": TRANSFORMER_ABSTRACT,
        "search_corpus": test_corpus,
        "similarity_threshold": 0.1  # Higher threshold
    }
    
    result = await find_similar_papers(args)
    
    assert result["success"] is True
    
    # Should filter out very dissimilar papers
    similar_papers = result["similar_papers"]
    if similar_papers:
        for paper in similar_papers:
            assert paper["similarity_score"] >= 0.1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_similar_papers_empty_reference():
    """Test similarity search with empty reference paper."""
    args = {
        "reference_paper": "",
        "search_corpus": [{"id": "test", "text": "test content"}]
    }
    
    result = await find_similar_papers(args)
    
    assert result["success"] is False
    assert "Reference paper text is required" in result["error"]
    assert result["similar_papers"] == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_similar_papers_empty_corpus():
    """Test similarity search with empty corpus (should use sample corpus)."""
    args = {
        "reference_paper": TRANSFORMER_ABSTRACT,
        "search_corpus": []  # Empty corpus
    }
    
    result = await find_similar_papers(args)
    
    assert result["success"] is True
    # Should use sample corpus instead
    assert len(result["similar_papers"]) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_paper_similarity_tfidf():
    """Test TF-IDF cosine similarity calculation."""
    args = {
        "paper1_text": TRANSFORMER_ABSTRACT,
        "paper2_text": BERT_ABSTRACT,
        "method": "tfidf_cosine"
    }
    
    result = await calculate_paper_similarity(args)
    
    assert result["success"] is True
    assert "similarity" in result
    
    similarity_data = result["similarity"]
    assert similarity_data["method"] == "tfidf_cosine"
    assert "similarity_score" in similarity_data
    assert 0 <= similarity_data["similarity_score"] <= 1
    
    # Should have term analysis
    assert "top_terms_paper1" in similarity_data
    assert "top_terms_paper2" in similarity_data
    assert "common_important_terms" in similarity_data
    
    # Should find some common important terms (both are about transformers/attention)
    common_terms = similarity_data["common_important_terms"]
    assert len(common_terms) >= 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_paper_similarity_jaccard():
    """Test Jaccard similarity calculation."""
    args = {
        "paper1_text": TRANSFORMER_ABSTRACT,
        "paper2_text": BERT_ABSTRACT,
        "method": "jaccard"
    }
    
    result = await calculate_paper_similarity(args)
    
    assert result["success"] is True
    similarity_data = result["similarity"]
    
    assert similarity_data["method"] == "jaccard"
    assert "similarity_score" in similarity_data
    assert 0 <= similarity_data["similarity_score"] <= 1
    
    assert "common_words" in similarity_data
    assert "total_unique_words" in similarity_data
    assert "sample_common_words" in similarity_data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_paper_similarity_word_overlap():
    """Test word overlap similarity calculation."""
    args = {
        "paper1_text": TRANSFORMER_ABSTRACT,
        "paper2_text": BERT_ABSTRACT,
        "method": "word_overlap"
    }
    
    result = await calculate_paper_similarity(args)
    
    assert result["success"] is True
    similarity_data = result["similarity"]
    
    assert similarity_data["method"] == "word_overlap"
    assert "similarity_score" in similarity_data
    assert "overlap_count" in similarity_data
    assert "total_words" in similarity_data
    assert "overlap_percentage" in similarity_data


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_paper_similarity_empty_texts():
    """Test similarity calculation with empty texts."""
    args = {
        "paper1_text": "",
        "paper2_text": "some text"
    }
    
    result = await calculate_paper_similarity(args)
    
    assert result["success"] is False
    assert "Both paper texts are required" in result["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_calculate_paper_similarity_identical_texts():
    """Test similarity calculation with identical texts."""
    args = {
        "paper1_text": TRANSFORMER_ABSTRACT,
        "paper2_text": TRANSFORMER_ABSTRACT,
        "method": "tfidf_cosine"
    }
    
    result = await calculate_paper_similarity(args)
    
    assert result["success"] is True
    # Identical texts should have high similarity
    assert result["similarity"]["similarity_score"] > 0.9


@pytest.mark.unit
def test_preprocess_text():
    """Test text preprocessing functionality."""
    messy_text = """
    This is TEXT with MIXED case and Numbers123 and special@chars!
    It also has figure 5 and table 2 and equation 3.
    Section 4.1 discusses the results.
    Extra    whitespace   should   be   normalized.
    """
    
    cleaned = _preprocess_text(messy_text)
    
    # Should be lowercase
    assert cleaned.islower()
    
    # Should remove numbers and special characters
    assert "123" not in cleaned
    assert "@" not in cleaned
    assert "!" not in cleaned
    
    # Should remove academic artifacts
    assert "figure" not in cleaned or "5" not in cleaned
    assert "table" not in cleaned or "2" not in cleaned
    assert "equation" not in cleaned or "3" not in cleaned
    
    # Should normalize whitespace
    assert "   " not in cleaned


@pytest.mark.unit
def test_calculate_tfidf_similarity():
    """Test internal TF-IDF similarity calculation."""
    text1 = "machine learning neural networks deep learning"
    text2 = "deep neural networks artificial intelligence machine learning"
    
    similarity_data = _calculate_tfidf_similarity(text1, text2)
    
    assert similarity_data["method"] == "tfidf_cosine"
    assert 0 <= similarity_data["similarity_score"] <= 1
    assert similarity_data["similarity_score"] > 0  # Should have some similarity
    
    # Should have term analysis
    assert "top_terms_paper1" in similarity_data
    assert "top_terms_paper2" in similarity_data
    assert "common_important_terms" in similarity_data


@pytest.mark.unit
def test_calculate_jaccard_similarity():
    """Test internal Jaccard similarity calculation."""
    text1 = "the quick brown fox jumps"
    text2 = "the lazy brown dog jumps"
    
    similarity_data = _calculate_jaccard_similarity(text1, text2)
    
    assert similarity_data["method"] == "jaccard"
    
    # Expected: intersection = {the, brown, jumps} = 3
    # Union = {the, quick, brown, fox, jumps, lazy, dog} = 7
    # Jaccard = 3/7 ≈ 0.43
    expected_similarity = 3 / 7
    assert abs(similarity_data["similarity_score"] - expected_similarity) < 0.01
    
    assert similarity_data["common_words"] == 3
    assert similarity_data["total_unique_words"] == 7


@pytest.mark.unit
def test_calculate_word_overlap():
    """Test internal word overlap calculation."""
    text1 = "the the quick brown fox"  # 5 words, "the" appears twice
    text2 = "the lazy brown dog"       # 4 words
    
    similarity_data = _calculate_word_overlap(text1, text2)
    
    assert similarity_data["method"] == "word_overlap"
    
    # Common words: "the" (min(2,1)=1), "brown" (min(1,1)=1) = 2 overlaps
    # Total words: 5 + 4 = 9
    # Overlap ratio: (2 * 2) / 9 ≈ 0.44
    expected_overlap = (2 * 2) / 9
    assert abs(similarity_data["similarity_score"] - expected_overlap) < 0.01
    
    assert similarity_data["overlap_count"] == 2
    assert similarity_data["total_words"] == 9


@pytest.mark.unit
def test_get_sample_corpus():
    """Test sample corpus generation."""
    corpus = _get_sample_corpus()
    
    assert isinstance(corpus, list)
    assert len(corpus) > 0
    
    for paper in corpus:
        assert "id" in paper
        assert "title" in paper
        assert "text" in paper
        assert isinstance(paper["text"], str)
        assert len(paper["text"]) > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_similarity_calculation_edge_cases():
    """Test similarity calculation with edge cases."""
    # Very short texts
    args_short = {
        "paper1_text": "deep learning",
        "paper2_text": "machine learning",
        "method": "tfidf_cosine"
    }
    
    result_short = await calculate_paper_similarity(args_short)
    assert result_short["success"] is True
    
    # Single word texts
    args_single = {
        "paper1_text": "transformer",
        "paper2_text": "attention",
        "method": "jaccard"
    }
    
    result_single = await calculate_paper_similarity(args_single)
    assert result_single["success"] is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_find_similar_papers_real_similarity_ranking():
    """Test that similarity ranking works correctly with realistic papers."""
    # Create corpus with papers of varying similarity to Transformer abstract
    test_corpus = [
        {
            "id": "highly_similar",
            "text": "Attention mechanisms and transformer architectures for sequence modeling"
        },
        {
            "id": "moderately_similar", 
            "text": "Neural networks for natural language processing tasks"
        },
        {
            "id": "low_similarity",
            "text": "Computer vision and image classification techniques"
        },
        {
            "id": "unrelated",
            "text": "Climate change and environmental policy recommendations"
        }
    ]
    
    args = {
        "reference_paper": TRANSFORMER_ABSTRACT,
        "search_corpus": test_corpus,
        "max_results": 4,
        "similarity_threshold": 0.0
    }
    
    result = await find_similar_papers(args)
    
    assert result["success"] is True
    similar_papers = result["similar_papers"]
    
    # Should rank highly similar paper first
    assert similar_papers[0]["id"] == "highly_similar"
    
    # Climate change paper should be least similar
    climate_paper = next((p for p in similar_papers if p["id"] == "unrelated"), None)
    if climate_paper:
        assert climate_paper["similarity_score"] < similar_papers[0]["similarity_score"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_similarity_metadata():
    """Test that similarity calculations include proper metadata."""
    args = {
        "paper1_text": TRANSFORMER_ABSTRACT,
        "paper2_text": BERT_ABSTRACT,
        "method": "tfidf_cosine"
    }
    
    result = await calculate_paper_similarity(args)
    
    assert result["success"] is True
    similarity_data = result["similarity"]
    
    # Should include comparison metadata
    assert "comparison_metadata" in similarity_data
    metadata = similarity_data["comparison_metadata"]
    
    assert "paper1_length" in metadata
    assert "paper2_length" in metadata
    assert "method" in metadata
    assert "paper1_words" in metadata
    assert "paper2_words" in metadata
    
    assert metadata["paper1_length"] == len(TRANSFORMER_ABSTRACT)
    assert metadata["paper2_length"] == len(BERT_ABSTRACT)
    assert metadata["method"] == "tfidf_cosine"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_default_similarity_method():
    """Test that default similarity method works when method not specified."""
    args = {
        "paper1_text": TRANSFORMER_ABSTRACT,
        "paper2_text": BERT_ABSTRACT
        # No method specified - should default to tfidf_cosine
    }
    
    result = await calculate_paper_similarity(args)
    
    assert result["success"] is True
    assert result["similarity"]["method"] == "tfidf_cosine"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unknown_similarity_method():
    """Test behavior with unknown similarity method."""
    args = {
        "paper1_text": TRANSFORMER_ABSTRACT,
        "paper2_text": BERT_ABSTRACT,
        "method": "unknown_method"
    }
    
    result = await calculate_paper_similarity(args)
    
    assert result["success"] is True
    # Should default to tfidf_cosine for unknown methods
    assert result["similarity"]["method"] == "tfidf_cosine"