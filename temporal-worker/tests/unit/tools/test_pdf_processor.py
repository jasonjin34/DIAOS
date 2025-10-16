"""
Tests for PDF processor tool with real PDF processing.
Tests PDF content extraction, section parsing, and text processing.
"""

import pytest
from unittest.mock import patch, Mock, MagicMock
import io
from src.tools.pdf_processor import (
    process_pdf_content,
    extract_paper_sections,
    _extract_paper_sections,
    _clean_extracted_text
)


# Sample academic paper text for section extraction
SAMPLE_ACADEMIC_TEXT = """
Title: Deep Learning Applications in Computer Vision

Abstract
This paper presents a comprehensive survey of deep learning applications in computer vision. 
We analyze various neural network architectures and their performance on image classification tasks.

1. Introduction
Computer vision has been revolutionized by deep learning techniques. Convolutional neural networks
(CNNs) have shown remarkable performance in various tasks including image classification, object detection,
and semantic segmentation.

2. Methodology
We conducted experiments using several deep learning frameworks including TensorFlow and PyTorch.
Our methodology involved training multiple CNN architectures on standard datasets.

2.1 Data Preprocessing
Images were preprocessed using standard techniques including normalization and data augmentation.

3. Results
The experimental results demonstrate significant improvements over traditional computer vision methods.
ResNet-50 achieved 92.3% accuracy on the ImageNet dataset.

4. Conclusion
Deep learning continues to push the boundaries of computer vision applications. Future work will
explore transformer-based architectures for vision tasks.

References
[1] LeCun, Y., et al. (2015). Deep learning. Nature, 521(7553), 436-444.
[2] He, K., et al. (2016). Deep residual learning for image recognition. CVPR.
"""


@pytest.mark.slow
@pytest.mark.arxiv
@pytest.mark.asyncio
async def test_process_pdf_content_real_arxiv_paper():
    """Test PDF processing with a real arXiv paper."""
    args = {
        "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",  # Attention Is All You Need
        "include_metadata": True
    }
    
    result = await process_pdf_content(args)
    
    assert result["success"] is True
    assert "content" in result
    
    content = result["content"]
    assert "full_text" in content
    assert "sections" in content
    assert "pages" in content
    assert "metadata" in content
    
    # Check that text was extracted
    assert len(content["full_text"]) > 1000  # Should have substantial content
    assert len(content["pages"]) > 5  # Multi-page paper
    
    # Check for common sections in academic papers
    sections = content["sections"]
    section_names = list(sections.keys())
    assert any("abstract" in name.lower() for name in section_names)
    
    # Verify processing metadata
    assert "processing_metadata" in result
    processing_meta = result["processing_metadata"]
    assert "file_size" in processing_meta
    assert "pages_processed" in processing_meta
    assert processing_meta["file_size"] > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_pdf_content_empty_url():
    """Test PDF processing with empty URL."""
    args = {
        "pdf_url": "",
        "include_metadata": True
    }
    
    result = await process_pdf_content(args)
    
    assert result["success"] is False
    assert "PDF URL is required" in result["error"]
    assert result["content"] == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_pdf_content_invalid_url():
    """Test PDF processing with invalid URL."""
    args = {
        "pdf_url": "https://invalid-url-that-does-not-exist.com/paper.pdf"
    }
    
    result = await process_pdf_content(args)
    
    assert result["success"] is False
    assert "error" in result
    assert result["content"] == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_pdf_content_mocked():
    """Test PDF processing with mocked dependencies."""
    # Mock response content
    mock_response = Mock()
    mock_response.content = b"fake pdf content"
    mock_response.raise_for_status.return_value = None
    
    # Mock PDF object
    mock_page = Mock()
    mock_page.extract_text.return_value = "Sample extracted text from page"
    
    mock_pdf = Mock()
    mock_pdf.pages = [mock_page, mock_page]  # Two pages
    mock_pdf.metadata = {
        "Title": "Test Paper",
        "Author": "Test Author",
        "Subject": "Test Subject"
    }
    mock_pdf.__enter__ = Mock(return_value=mock_pdf)
    mock_pdf.__exit__ = Mock(return_value=None)
    
    with patch('src.tools.pdf_processor.requests.get', return_value=mock_response), \
         patch('src.tools.pdf_processor.pdfplumber.open', return_value=mock_pdf):
        
        args = {
            "pdf_url": "https://example.com/test.pdf",
            "include_metadata": True
        }
        
        result = await process_pdf_content(args)
        
        assert result["success"] is True
        content = result["content"]
        
        assert "Sample extracted text from page" in content["full_text"]
        assert len(content["pages"]) == 2
        assert content["metadata"]["title"] == "Test Paper"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_paper_sections_comprehensive():
    """Test section extraction with comprehensive academic text."""
    args = {
        "paper_text": SAMPLE_ACADEMIC_TEXT,
        "sections": ["abstract", "introduction", "methodology", "results", "conclusion", "references"],
        "strict_matching": False
    }
    
    result = await extract_paper_sections(args)
    
    assert result["success"] is True
    assert "sections" in result
    
    sections = result["sections"]
    
    # Should find most common sections
    assert "abstract" in sections
    assert "introduction" in sections
    assert "methodology" in sections
    assert "results" in sections
    assert "conclusion" in sections
    assert "references" in sections
    
    # Check section content
    abstract_content = sections["abstract"]["content"]
    assert "comprehensive survey" in abstract_content
    assert "neural network architectures" in abstract_content
    
    introduction_content = sections["introduction"]["content"]
    assert "Computer vision" in introduction_content
    assert "Convolutional neural networks" in introduction_content
    
    # Check metadata
    assert "extraction_metadata" in result
    metadata = result["extraction_metadata"]
    assert metadata["sections_requested"] == 6
    assert metadata["sections_found"] >= 5  # Should find most sections


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_paper_sections_strict_matching():
    """Test section extraction with strict matching."""
    text_with_exact_headers = """
Abstract
This is the abstract section.

Introduction
This is the introduction section.

Methodology
This is the methodology section.
"""
    
    args = {
        "paper_text": text_with_exact_headers,
        "sections": ["Abstract", "Introduction", "Methodology"],
        "strict_matching": True
    }
    
    result = await extract_paper_sections(args)
    
    assert result["success"] is True
    sections = result["sections"]
    
    # With strict matching, should find exact matches
    assert len(sections) >= 2  # Should find at least some sections


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_paper_sections_empty_text():
    """Test section extraction with empty text."""
    args = {
        "paper_text": "",
        "sections": ["abstract", "introduction"]
    }
    
    result = await extract_paper_sections(args)
    
    assert result["success"] is False
    assert "Paper text is required" in result["error"]
    assert result["sections"] == {}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_paper_sections_no_sections_found():
    """Test section extraction when no sections are found."""
    args = {
        "paper_text": "This is just plain text without any recognizable section headers.",
        "sections": ["abstract", "introduction", "conclusion"]
    }
    
    result = await extract_paper_sections(args)
    
    assert result["success"] is True
    assert result["sections"] == {}  # No sections found
    assert result["extraction_metadata"]["sections_found"] == 0


@pytest.mark.unit
def test_extract_paper_sections_helper():
    """Test the internal section extraction helper function."""
    text = """
Abstract
This is the abstract content.

1. Introduction
This is the introduction content.

2. Methods
This is the methods content.

Conclusion
This is the conclusion content.
"""
    
    sections = _extract_paper_sections(text, ["abstract", "introduction", "methods", "conclusion"])
    
    assert "abstract" in sections
    assert "introduction" in sections
    assert "methods" in sections
    assert "conclusion" in sections
    
    # Check content structure
    abstract_section = sections["abstract"]
    assert "content" in abstract_section
    assert "header" in abstract_section
    assert "word_count" in abstract_section
    assert "char_count" in abstract_section
    
    assert "abstract content" in abstract_section["content"]
    assert abstract_section["word_count"] > 0


@pytest.mark.unit
def test_extract_paper_sections_numbered_headers():
    """Test extraction with numbered section headers."""
    text = """
1. Introduction
This is the introduction section with some content.

2. Background
This section covers the background material.

3.1 Methodology Overview
This subsection describes our approach.

4. Results
The experimental results are presented here.
"""
    
    sections = _extract_paper_sections(text, ["introduction", "background", "methodology", "results"])
    
    assert "introduction" in sections
    assert "background" in sections
    assert "methodology" in sections
    assert "results" in sections
    
    # Check that content doesn't include the next section header
    intro_content = sections["introduction"]["content"]
    assert "Background" not in intro_content
    assert "introduction section" in intro_content


@pytest.mark.unit
def test_clean_extracted_text():
    """Test text cleaning functionality."""
    messy_text = """This   is  text   with    excessive    whitespace.
    
    
    It also has weird line breaks and 
    hyphen-
    ated words that got broken.
    
    Page 123
    
    More content here.
    Page 456 of something
    """
    
    cleaned = _clean_extracted_text(messy_text)
    
    # Should normalize whitespace
    assert "excessive    whitespace" not in cleaned
    assert "excessive whitespace" in cleaned
    
    # Should fix hyphenated words
    assert "hyphenated" in cleaned
    assert "hyphen-\n    ated" not in cleaned
    
    # Should remove page numbers
    assert "Page 123" not in cleaned
    assert "Page 456" not in cleaned


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_pdf_content_custom_sections():
    """Test PDF processing with custom section list."""
    mock_response = Mock()
    mock_response.content = b"fake pdf content"
    mock_response.raise_for_status.return_value = None
    
    mock_page = Mock()
    mock_page.extract_text.return_value = SAMPLE_ACADEMIC_TEXT
    
    mock_pdf = Mock()
    mock_pdf.pages = [mock_page]
    mock_pdf.metadata = {}
    mock_pdf.__enter__ = Mock(return_value=mock_pdf)
    mock_pdf.__exit__ = Mock(return_value=None)
    
    with patch('src.tools.pdf_processor.requests.get', return_value=mock_response), \
         patch('src.tools.pdf_processor.pdfplumber.open', return_value=mock_pdf):
        
        args = {
            "pdf_url": "https://example.com/test.pdf",
            "sections": ["abstract", "introduction", "conclusion"]
        }
        
        result = await process_pdf_content(args)
        
        assert result["success"] is True
        sections = result["content"]["sections"]
        
        # Should only extract requested sections
        section_names = list(sections.keys())
        for name in section_names:
            assert name in ["abstract", "introduction", "conclusion"]


@pytest.mark.unit
def test_section_extraction_edge_cases():
    """Test section extraction with edge cases."""
    # Test with mixed case and special formatting
    text = """
ABSTRACT
Content in uppercase header.

Introduction
Regular case header.

METHODOLOGY
Another uppercase header.

2. results
Numbered lowercase header.

3.Discussion and Conclusion
Multi-word header with number.
"""
    
    sections = _extract_paper_sections(
        text, 
        ["abstract", "introduction", "methodology", "results", "conclusion"], 
        strict_matching=False
    )
    
    # Should handle case variations
    assert "abstract" in sections
    assert "introduction" in sections
    assert "methodology" in sections
    assert "results" in sections


@pytest.mark.unit
@pytest.mark.asyncio
async def test_extract_sections_with_subsections():
    """Test section extraction handling subsections."""
    text_with_subsections = """
1. Introduction
Main introduction content.

1.1 Background
Subsection content.

1.2 Motivation
Another subsection.

2. Methodology
Main methodology content.

2.1 Data Collection
Methodology subsection.
"""
    
    args = {
        "paper_text": text_with_subsections,
        "sections": ["introduction", "methodology"]
    }
    
    result = await extract_paper_sections(args)
    
    assert result["success"] is True
    sections = result["sections"]
    
    # Should capture main sections
    assert "introduction" in sections
    assert "methodology" in sections
    
    # Introduction should include subsections until next main section
    intro_content = sections["introduction"]["content"]
    assert "Background" in intro_content
    assert "Motivation" in intro_content
    assert "Data Collection" not in intro_content  # Should be in methodology


@pytest.mark.slow
@pytest.mark.arxiv
@pytest.mark.asyncio
async def test_process_pdf_content_timeout_handling():
    """Test PDF processing with timeout scenarios."""
    args = {
        "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
        "include_metadata": False  # Faster processing
    }
    
    # Should handle real request within reasonable time
    result = await process_pdf_content(args)
    
    # Even if slow, should eventually succeed or fail gracefully
    assert "success" in result
    assert "content" in result or "error" in result