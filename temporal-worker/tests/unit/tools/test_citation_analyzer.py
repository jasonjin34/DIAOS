"""
Tests for citation analyzer tool with real text processing.
Tests citation extraction, network analysis, and pattern recognition.
"""

import pytest
from src.tools.citation_analyzer import (
    extract_citations,
    analyze_citation_network,
    _simulate_cited_papers,
    _simulate_citing_papers,
    _calculate_network_density,
    _find_central_papers,
    _analyze_co_citations
)


# Sample academic text with various citation formats
SAMPLE_PAPER_TEXT = """
Abstract: Machine learning has shown remarkable progress in recent years (LeCun et al., 2015). 
Deep neural networks have revolutionized computer vision (Krizhevsky et al., 2012) and natural 
language processing (Vaswani et al., 2017). The attention mechanism proposed by Bahdanau et al. (2014) 
has become fundamental to modern architectures.

Introduction: Building on the work of Goodfellow et al. (2014) on generative adversarial networks, 
researchers have developed numerous extensions [1, 2, 3]. The transformer architecture (Vaswani et al., 2017) 
introduced in "Attention Is All You Need" has been particularly influential. Recent work by Brown et al. (2020) 
on GPT-3 demonstrates the scaling properties of these models.

The paper references several DOIs: doi:10.1038/nature14539 and arXiv:1706.03762. Additional work 
includes references to arXiv:2005.14165 and doi:10.1145/3219819.3220081.

References:
[1] Radford et al. (2018). Improving language understanding by generative pre-training.
[2] Devlin et al. (2018). BERT: Pre-training of deep bidirectional transformers.
[3] Liu et al. (2019). RoBERTa: A robustly optimized BERT pretraining approach.
"""

MINIMAL_TEXT = """
Recent advances in AI (Smith, 2023) and ML (Jones et al., 2022) show promise.
References: [1] Brown (2021), [2] Davis (2020).
arXiv:2301.00001 and doi:10.1000/test are relevant.
"""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_citations_comprehensive():
    """Test citation extraction with comprehensive academic text."""
    args = {
        "paper_text": SAMPLE_PAPER_TEXT,
        "format": "mixed"
    }
    
    result = await extract_citations(args)
    
    assert result["success"] is True
    assert "citations" in result
    assert result["count"] > 0
    
    citations = result["citations"]
    
    # Check for different citation types
    citation_types = {c["type"] for c in citations}
    assert "author_year" in citation_types
    assert "numbered" in citation_types
    assert "doi" in citation_types
    assert "arxiv" in citation_types
    
    # Verify specific citations
    author_year_citations = [c for c in citations if c["type"] == "author_year"]
    assert any("LeCun" in c["author"] and c["year"] == "2015" for c in author_year_citations)
    assert any("Vaswani" in c["author"] and c["year"] == "2017" for c in author_year_citations)
    
    # Check DOI citations
    doi_citations = [c for c in citations if c["type"] == "doi"]
    assert any("10.1038/nature14539" in c["doi"] for c in doi_citations)
    
    # Check arXiv citations
    arxiv_citations = [c for c in citations if c["type"] == "arxiv"]
    assert any("1706.03762" in c["arxiv_id"] for c in arxiv_citations)
    assert any("2005.14165" in c["arxiv_id"] for c in arxiv_citations)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_citations_minimal_text():
    """Test citation extraction with minimal text."""
    args = {
        "paper_text": MINIMAL_TEXT
    }
    
    result = await extract_citations(args)
    
    assert result["success"] is True
    citations = result["citations"]
    
    # Should find author-year citations
    author_citations = [c for c in citations if c["type"] == "author_year"]
    assert any("Smith" in c["author"] and c["year"] == "2023" for c in author_citations)
    assert any("Jones" in c["author"] and c["year"] == "2022" for c in author_citations)
    
    # Should find numbered citations
    numbered_citations = [c for c in citations if c["type"] == "numbered"]
    assert len(numbered_citations) >= 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_citations_empty_text():
    """Test citation extraction with empty text."""
    args = {
        "paper_text": ""
    }
    
    result = await extract_citations(args)
    
    assert result["success"] is False
    assert "Either paper_text or paper_url is required" in result["error"]
    assert result["citations"] == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_citations_url_provided():
    """Test citation extraction with URL provided."""
    args = {
        "paper_url": "https://example.com/paper.pdf"
    }
    
    result = await extract_citations(args)
    
    assert result["success"] is True
    # Should handle URL case (simplified in current implementation)
    assert "citations" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_citations_no_citations():
    """Test citation extraction with text containing no citations."""
    args = {
        "paper_text": "This is just plain text with no citations or references at all."
    }
    
    result = await extract_citations(args)
    
    assert result["success"] is True
    assert result["count"] == 0
    assert result["citations"] == []


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_citation_network_basic():
    """Test basic citation network analysis."""
    args = {
        "paper_ids": ["paper1", "paper2", "paper3"],
        "depth": 2,
        "include_co_citations": True
    }
    
    result = await analyze_citation_network(args)
    
    assert result["success"] is True
    assert "network" in result
    
    network = result["network"]
    assert "nodes" in network
    assert "edges" in network
    assert "metrics" in network
    
    # Should have nodes for all input papers
    assert len(network["nodes"]) >= 3
    paper_ids = {node["id"] for node in network["nodes"]}
    assert "paper1" in paper_ids
    assert "paper2" in paper_ids
    assert "paper3" in paper_ids
    
    # Check metrics
    metrics = network["metrics"]
    assert "total_nodes" in metrics
    assert "total_edges" in metrics
    assert "network_density" in metrics
    assert "central_papers" in metrics


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_citation_network_single_paper():
    """Test citation network analysis with single paper."""
    args = {
        "paper_ids": ["single_paper"],
        "depth": 1
    }
    
    result = await analyze_citation_network(args)
    
    assert result["success"] is True
    network = result["network"]
    
    # Should have at least the input paper as a node
    assert len(network["nodes"]) >= 1
    assert any(node["id"] == "single_paper" for node in network["nodes"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_citation_network_empty_list():
    """Test citation network analysis with empty paper list."""
    args = {
        "paper_ids": [],
        "depth": 2
    }
    
    result = await analyze_citation_network(args)
    
    assert result["success"] is False
    assert "At least one paper ID is required" in result["error"]
    assert result["network"] == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_analyze_citation_network_co_citations():
    """Test citation network with co-citation analysis."""
    args = {
        "paper_ids": ["paper_a", "paper_b"],
        "depth": 2,
        "include_co_citations": True
    }
    
    result = await analyze_citation_network(args)
    
    assert result["success"] is True
    network = result["network"]
    
    # Should include co-citation analysis
    assert "co_citations" in network
    co_citations = network["co_citations"]
    assert "co_citation_pairs" in co_citations
    assert "strongest_co_citations" in co_citations


@pytest.mark.unit
def test_simulate_cited_papers():
    """Test the citation simulation helper function."""
    cited_papers = _simulate_cited_papers("test_paper", 2)
    
    assert isinstance(cited_papers, list)
    assert len(cited_papers) <= 4  # min(5, 2 * 2)
    
    for paper_id, relationship in cited_papers:
        assert isinstance(paper_id, str)
        assert relationship == "direct_citation"
        assert "cited_" in paper_id


@pytest.mark.unit
def test_simulate_citing_papers():
    """Test the citing papers simulation helper function."""
    citing_papers = _simulate_citing_papers("test_paper", 3)
    
    assert isinstance(citing_papers, list)
    assert len(citing_papers) <= 3  # min(3, 3)
    
    for paper_id, relationship in citing_papers:
        assert isinstance(paper_id, str)
        assert relationship == "direct_citation"
        assert "citing_" in paper_id


@pytest.mark.unit
def test_calculate_network_density():
    """Test network density calculation."""
    # Test with simple network
    network = {
        "nodes": [{"id": "1"}, {"id": "2"}, {"id": "3"}],
        "edges": [{"source": "1", "target": "2"}, {"source": "2", "target": "3"}]
    }
    
    density = _calculate_network_density(network)
    
    # 3 nodes, 2 edges, possible edges = 3 * 2 = 6
    expected_density = 2 / 6
    assert abs(density - expected_density) < 0.001
    
    # Test with no edges
    network_no_edges = {
        "nodes": [{"id": "1"}, {"id": "2"}],
        "edges": []
    }
    
    density_no_edges = _calculate_network_density(network_no_edges)
    assert density_no_edges == 0.0
    
    # Test with single node
    network_single = {
        "nodes": [{"id": "1"}],
        "edges": []
    }
    
    density_single = _calculate_network_density(network_single)
    assert density_single == 0.0


@pytest.mark.unit
def test_find_central_papers():
    """Test finding central papers in citation network."""
    network = {
        "edges": [
            {"source": "A", "target": "central"},
            {"source": "B", "target": "central"},
            {"source": "C", "target": "central"},
            {"source": "D", "target": "other"},
            {"source": "E", "target": "other"}
        ]
    }
    
    central_papers = _find_central_papers(network)
    
    assert isinstance(central_papers, list)
    assert len(central_papers) <= 5
    
    # "central" should be most cited
    if central_papers:
        most_central = central_papers[0]
        assert most_central["paper_id"] == "central"
        assert most_central["citation_count"] == 3
        assert most_central["centrality_rank"] == 1


@pytest.mark.unit
def test_analyze_co_citations():
    """Test co-citation analysis functionality."""
    network = {
        "edges": [
            {"source": "paper1", "target": "cited_a"},
            {"source": "paper1", "target": "cited_b"},
            {"source": "paper2", "target": "cited_a"},
            {"source": "paper2", "target": "cited_b"},
            {"source": "paper3", "target": "cited_c"}
        ]
    }
    
    co_citations = _analyze_co_citations(network)
    
    assert "co_citation_pairs" in co_citations
    assert "strongest_co_citations" in co_citations
    
    # Should find co-citation between paper1 and paper2
    strongest = co_citations["strongest_co_citations"]
    if strongest:
        top_pair = strongest[0]
        assert "papers" in top_pair
        assert "shared_citations" in top_pair
        assert "shared_papers" in top_pair
        assert top_pair["shared_citations"] >= 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_citation_extraction_edge_cases():
    """Test citation extraction with edge cases."""
    # Test with special characters and formatting
    special_text = """
    See (O'Connor & Smith, 2023) and (González-López et al., 2022).
    Also [10], [100] and references like doi:10.1234/special-chars_test.
    arXiv papers: arXiv:2301.12345 and arXiv:1234.5678v2.
    """
    
    args = {"paper_text": special_text}
    result = await extract_citations(args)
    
    assert result["success"] is True
    citations = result["citations"]
    
    # Should handle special characters in author names
    author_citations = [c for c in citations if c["type"] == "author_year"]
    assert any("Connor" in c["author"] or "González" in c["author"] for c in author_citations)
    
    # Should handle multi-digit reference numbers
    numbered_citations = [c for c in citations if c["type"] == "numbered"]
    assert any(c["reference_number"] == "100" for c in numbered_citations)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_citation_network_with_depth():
    """Test citation network analysis with different depths."""
    # Test depth 1
    args_depth_1 = {
        "paper_ids": ["main_paper"],
        "depth": 1
    }
    
    result_depth_1 = await analyze_citation_network(args_depth_1)
    nodes_depth_1 = len(result_depth_1["network"]["nodes"])
    
    # Test depth 3
    args_depth_3 = {
        "paper_ids": ["main_paper"],
        "depth": 3
    }
    
    result_depth_3 = await analyze_citation_network(args_depth_3)
    nodes_depth_3 = len(result_depth_3["network"]["nodes"])
    
    # Higher depth should generally result in more nodes
    assert nodes_depth_3 >= nodes_depth_1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_citations_metadata():
    """Test that citation extraction returns proper metadata."""
    args = {"paper_text": SAMPLE_PAPER_TEXT}
    result = await extract_citations(args)
    
    assert "extraction_metadata" in result
    metadata = result["extraction_metadata"]
    
    assert "text_length" in metadata
    assert "patterns_used" in metadata
    assert "format" in metadata
    
    assert metadata["text_length"] == len(SAMPLE_PAPER_TEXT)
    assert isinstance(metadata["patterns_used"], list)
    assert len(metadata["patterns_used"]) == 4  # author_year, numbered, doi, arxiv