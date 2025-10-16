"""
Pytest configuration and fixtures for temporal-worker tests.
Provides shared fixtures, test data, and configuration for all test modules.
"""

import pytest
import os
import asyncio
from typing import Dict, Any, List


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_paper_abstract():
    """Sample academic paper abstract for testing."""
    return """
    We present a novel approach to deep learning that leverages attention mechanisms
    for improved performance on natural language processing tasks. Our method, called
    the Transformer, relies entirely on attention mechanisms and eschews recurrence
    and convolutions entirely. Experiments on machine translation tasks show that
    these models are superior in quality while being more parallelizable and requiring
    significantly less time to train.
    """


@pytest.fixture
def sample_arxiv_paper_ids():
    """Well-known arXiv paper IDs for testing with real API."""
    return {
        "transformer": "1706.03762",  # Attention Is All You Need
        "bert": "1810.04805",         # BERT
        "gpt": "1706.03762",          # Using transformer paper as backup
        "resnet": "1512.03385",       # Deep Residual Learning for Image Recognition
        "invalid": "9999.99999"       # Invalid paper ID for error testing
    }


@pytest.fixture
def sample_citation_text():
    """Sample text with various citation formats for testing."""
    return """
    Recent advances in deep learning (LeCun et al., 2015) have revolutionized
    natural language processing. The transformer architecture (Vaswani et al., 2017)
    has been particularly influential. Prior work on attention mechanisms [1, 2, 3]
    laid the groundwork for these developments.
    
    References include doi:10.1038/nature14539 and arXiv:1706.03762.
    
    [1] Bahdanau et al. (2014). Neural machine translation by jointly learning to align and translate.
    [2] Luong et al. (2015). Effective approaches to attention-based neural machine translation.
    [3] Chorowski et al. (2015). Attention-based models for speech recognition.
    """


@pytest.fixture
def sample_paper_corpus():
    """Sample corpus of papers for similarity testing."""
    return [
        {
            "id": "nlp_transformer",
            "title": "Attention Is All You Need",
            "text": "The Transformer model architecture relies entirely on attention mechanisms."
        },
        {
            "id": "nlp_bert", 
            "title": "BERT: Pre-training Deep Bidirectional Transformers",
            "text": "BERT uses bidirectional transformers for language understanding tasks."
        },
        {
            "id": "cv_resnet",
            "title": "Deep Residual Learning for Image Recognition", 
            "text": "ResNet introduces residual connections for training very deep neural networks."
        },
        {
            "id": "cv_cnn",
            "title": "Convolutional Neural Networks for Visual Recognition",
            "text": "CNNs apply convolution operations for computer vision and image classification."
        },
        {
            "id": "other_climate",
            "title": "Climate Change Impact Assessment",
            "text": "Climate change affects global temperature patterns and weather systems."
        }
    ]


@pytest.fixture
def mock_pdf_content():
    """Mock PDF content for testing PDF processing."""
    return {
        "pages": [
            {
                "page_number": 1,
                "text": """
                Title: Deep Learning Applications
                
                Abstract
                This paper presents applications of deep learning in various domains.
                """
            },
            {
                "page_number": 2, 
                "text": """
                1. Introduction
                Deep learning has shown remarkable success in recent years.
                
                2. Methodology
                We employ convolutional neural networks for our experiments.
                """
            },
            {
                "page_number": 3,
                "text": """
                3. Results
                Our experiments show significant improvements over baseline methods.
                
                4. Conclusion
                Deep learning continues to advance the state of the art.
                """
            }
        ],
        "metadata": {
            "title": "Deep Learning Applications",
            "author": "Test Author",
            "pages": 3
        }
    }


@pytest.fixture
def sample_tool_args():
    """Sample arguments for different tools."""
    return {
        "arxiv_search": {
            "query": "machine learning",
            "max_results": 5,
            "category": "cs.AI"
        },
        "arxiv_paper_details": {
            "paper_id": "1706.03762"
        },
        "extract_citations": {
            "paper_text": "Sample paper with citations (Smith et al., 2020)."
        },
        "process_pdf": {
            "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf"
        },
        "find_similar_papers": {
            "reference_paper": "Deep learning and neural networks",
            "max_results": 3
        },
        "calculate_similarity": {
            "paper1_text": "Deep learning for NLP",
            "paper2_text": "Neural networks for language processing"
        },
        "analyze_citation_network": {
            "paper_ids": ["paper1", "paper2"],
            "depth": 2
        },
        "extract_sections": {
            "paper_text": "Abstract\nThis is abstract.\n\nIntroduction\nThis is intro.",
            "sections": ["abstract", "introduction"]
        }
    }


@pytest.fixture
def test_environment_info():
    """Information about the test environment."""
    return {
        "has_internet": True,  # Assume internet access for API tests
        "arxiv_api_available": True,
        "openai_api_key": os.getenv("OPENAI_API_KEY") is not None,
        "test_mode": "real_api"  # vs "mocked"
    }


@pytest.fixture
def citation_network_sample():
    """Sample citation network data for testing."""
    return {
        "nodes": [
            {"id": "paper1", "type": "paper", "properties": {"title": "Paper 1"}},
            {"id": "paper2", "type": "paper", "properties": {"title": "Paper 2"}},
            {"id": "cited1", "type": "cited_paper", "properties": {"title": "Cited Paper 1"}},
            {"id": "cited2", "type": "cited_paper", "properties": {"title": "Cited Paper 2"}}
        ],
        "edges": [
            {"source": "paper1", "target": "cited1", "type": "cites"},
            {"source": "paper1", "target": "cited2", "type": "cites"},
            {"source": "paper2", "target": "cited1", "type": "cites"}
        ],
        "metrics": {
            "total_nodes": 4,
            "total_edges": 3,
            "network_density": 0.25
        }
    }


# Pytest markers configuration
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (slower, real APIs)"
    )
    config.addinivalue_line(
        "markers", "slow: Slow tests that may take time"
    )
    config.addinivalue_line(
        "markers", "arxiv: Tests that require arXiv API access"
    )
    config.addinivalue_line(
        "markers", "openai: Tests that require OpenAI API access"
    )
    config.addinivalue_line(
        "markers", "temporal: Tests that require Temporal server"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their characteristics."""
    for item in items:
        # Mark tests that use real arXiv API
        if "arxiv" in item.name.lower() or any("arxiv" in marker.name for marker in item.iter_markers()):
            item.add_marker(pytest.mark.slow)
        
        # Mark PDF processing tests as slow
        if "pdf" in item.name.lower() and "real" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)


# Skip tests based on environment
def pytest_runtest_setup(item):
    """Skip tests based on environment conditions."""
    # Skip arXiv tests if no internet (could be enhanced with actual connectivity check)
    if item.get_closest_marker("arxiv"):
        if not os.getenv("ALLOW_ARXIV_TESTS", "true").lower() == "true":
            pytest.skip("arXiv API tests disabled")
    
    # Skip OpenAI tests if no API key
    if item.get_closest_marker("openai"):
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("OpenAI API key not available")
    
    # Skip temporal tests if no temporal server
    if item.get_closest_marker("temporal"):
        if not os.getenv("TEMPORAL_SERVER_AVAILABLE", "false").lower() == "true":
            pytest.skip("Temporal server not available")


@pytest.fixture
def similarity_test_papers():
    """Pairs of papers with known similarity relationships for testing."""
    return {
        "high_similarity": {
            "paper1": "Transformer architecture for natural language processing using attention mechanisms",
            "paper2": "Attention-based neural networks for language understanding and machine translation"
        },
        "medium_similarity": {
            "paper1": "Deep learning for computer vision and image recognition tasks",
            "paper2": "Neural networks and machine learning algorithms for data analysis"
        },
        "low_similarity": {
            "paper1": "Quantum computing algorithms and quantum information theory",
            "paper2": "Climate change modeling and environmental impact assessment"
        }
    }


@pytest.fixture
def academic_text_sections():
    """Well-formatted academic text with clear sections for testing."""
    return """
Title: Advanced Machine Learning Techniques

Abstract
This paper presents novel approaches to machine learning that improve upon existing methods.
We demonstrate significant performance gains across multiple benchmark datasets.

1. Introduction
Machine learning has become increasingly important in recent years. Traditional approaches
often suffer from limitations in scalability and generalization.

2. Related Work
Previous research in this area includes work by Smith et al. (2020) and Jones et al. (2021).
These studies laid the foundation for our current investigation.

3. Methodology
Our approach combines multiple techniques:
- Deep neural networks
- Attention mechanisms  
- Regularization strategies

3.1 Data Preprocessing
We preprocess the data using standard normalization techniques.

3.2 Model Architecture
The model consists of multiple layers with residual connections.

4. Experiments
We conducted experiments on three datasets: ImageNet, CIFAR-10, and MNIST.

4.1 Experimental Setup
All experiments used the same hyperparameters for fair comparison.

4.2 Results
Our method achieves state-of-the-art performance on all benchmarks.

5. Conclusion
This work demonstrates the effectiveness of our proposed approach.
Future work will explore applications to other domains.

References
[1] Smith, J. et al. (2020). Deep Learning Fundamentals.
[2] Jones, M. et al. (2021). Advanced Neural Architectures.
"""