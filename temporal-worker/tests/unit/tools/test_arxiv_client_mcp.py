"""
Tests for enhanced arXiv client using arxiv-mcp-server.
Tests enhanced search, local storage, paper management, and caching functionality.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from unittest.mock import patch, Mock
from src.tools.arxiv_client_mcp import (
    ArxivMCPServerClient as ArxivMCPClient,
    arxiv_search_papers,
    arxiv_download_paper,
    arxiv_list_papers,
    arxiv_read_paper,
    arxiv_get_paper_metadata
)


@pytest.fixture
def temp_storage():
    """Create temporary storage directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mcp_client(temp_storage):
    """Create MCP client with temporary storage."""
    return ArxivMCPClient(storage_path=temp_storage)


@pytest.mark.unit
def test_arxiv_mcp_client_initialization(temp_storage):
    """Test MCP client initialization."""
    client = ArxivMCPClient(storage_path=temp_storage)
    
    assert client.storage_path == Path(temp_storage)
    assert client.storage_path.exists()
    assert client.papers_index == {}
    assert client.papers_index_file.exists()


@pytest.mark.unit
def test_arxiv_mcp_client_papers_index(mcp_client):
    """Test papers index loading and saving."""
    # Add test data to index
    test_data = {
        "1706.03762": {
            "title": "Attention Is All You Need",
            "download_date": "2024-01-01T00:00:00",
            "file_size": 1234567,
            "categories": ["cs.CL", "cs.AI"]
        }
    }
    
    mcp_client.papers_index = test_data
    mcp_client._save_papers_index()
    
    # Create new client to test loading
    new_client = ArxivMCPClient(storage_path=str(mcp_client.storage_path))
    assert new_client.papers_index == test_data


@pytest.mark.arxiv
@pytest.mark.asyncio
async def test_arxiv_search_papers_enhanced():
    """Test enhanced arXiv search with advanced filtering."""
    args = {
        "query": "attention mechanism transformer",
        "max_results": 5,
        "category": "cs.AI",
        "date_from": "2017-01-01",
        "sort_by": "relevance"
    }
    
    result = await arxiv_search_papers(args)
    
    assert result["success"] is True
    assert "papers" in result
    assert isinstance(result["papers"], list)
    assert len(result["papers"]) <= 5
    
    # Check enhanced metadata
    if result["papers"]:
        paper = result["papers"][0]
        assert "id" in paper
        assert "title" in paper
        assert "authors" in paper
        assert "is_downloaded" in paper
        assert "local_path" in paper or paper["local_path"] is None
        assert "primary_category" in paper
        assert "entry_url" in paper
    
    # Check search metadata
    metadata = result["search_metadata"]
    assert metadata["category_filter"] == "cs.AI"
    assert metadata["date_from"] == "2017-01-01"
    assert metadata["sort_by"] == "relevance"
    assert "storage_path" in metadata


@pytest.mark.unit
@pytest.mark.asyncio
async def test_arxiv_search_papers_empty_query():
    """Test enhanced search with empty query."""
    args = {"query": ""}
    
    result = await arxiv_search_papers(args)
    
    assert result["success"] is False
    assert "Search query is required" in result["error"]
    assert result["papers"] == []



@pytest.mark.arxiv
@pytest.mark.slow
@pytest.mark.asyncio
async def test_arxiv_download_paper_real(mcp_client):
    """Test downloading a real arXiv paper."""
    # Use the storage path from our test client
    with patch('src.tools.arxiv_client_mcp.mcp_client', mcp_client):
        args = {
            "paper_id": "1706.03762"  # Attention Is All You Need
        }
        
        result = await arxiv_download_paper(args)
        
        assert result["success"] is True
        assert result["paper_id"] == "1706.03762"
        assert "local_path" in result
        assert "metadata_path" in result
        assert "file_size" in result
        assert result["file_size"] > 0
        
        # Verify files were created
        paper_file = Path(result["local_path"])
        metadata_file = Path(result["metadata_path"])
        assert paper_file.exists()
        assert metadata_file.exists()
        
        # Verify metadata content
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        assert metadata["id"] == "1706.03762"
        assert "attention" in metadata["title"].lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_arxiv_download_paper_already_exists(mcp_client):
    """Test downloading when paper already exists."""
    with patch('src.tools.arxiv_client_mcp.mcp_client', mcp_client):
        paper_id = "test.paper"
        
        # Create fake existing file
        paper_file = mcp_client._get_paper_file_path(paper_id)
        paper_file.write_text("fake pdf content")
        
        args = {"paper_id": paper_id}
        result = await arxiv_download_paper(args)
        
        assert result["success"] is True
        assert result["status"] == "already_downloaded"
        assert result["paper_id"] == paper_id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_arxiv_download_paper_force_redownload(mcp_client):
    """Test force re-download of existing paper."""
    with patch('src.tools.arxiv_client_mcp.mcp_client', mcp_client):
        paper_id = "1706.03762"
        
        # Create fake existing file
        paper_file = mcp_client._get_paper_file_path(paper_id)
        paper_file.write_text("old content")
        
        with patch('src.tools.arxiv_client_mcp._async_arxiv_search') as mock_search, \
             patch('src.tools.arxiv_client_mcp.requests.get') as mock_get:
            
            # Mock arXiv result
            mock_result = Mock()
            mock_result.entry_id = f"https://arxiv.org/abs/{paper_id}"
            mock_result.title = "Test Paper"
            mock_result.authors = [Mock(name="Test Author")]
            mock_result.summary = "Test abstract"
            mock_result.published = None
            mock_result.updated = None
            mock_result.categories = ["cs.AI"]
            mock_result.primary_category = "cs.AI"
            mock_result.pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
            mock_result.doi = None
            mock_result.journal_ref = None
            mock_result.comment = None
            
            async def mock_async_search(search):
                yield mock_result
            mock_search.side_effect = mock_async_search
            
            # Mock HTTP response
            mock_response = Mock()
            mock_response.content = b"new pdf content"
            mock_response.iter_content.return_value = [b"new pdf content"]
            mock_get.return_value = mock_response
            
            args = {
                "paper_id": paper_id,
                "force_download": True
            }
            
            result = await arxiv_download_paper(args)
            
            assert result["success"] is True
            assert result["status"] == "downloaded"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_arxiv_list_papers(mcp_client):
    """Test listing downloaded papers."""
    with patch('src.tools.arxiv_client_mcp.mcp_client', mcp_client):
        # Add test papers to index
        test_papers = {
            "1706.03762": {
                "title": "Attention Is All You Need",
                "download_date": "2024-01-01T00:00:00",
                "file_size": 1000000,
                "categories": ["cs.CL", "cs.AI"]
            },
            "1810.04805": {
                "title": "BERT Paper",
                "download_date": "2024-01-02T00:00:00",
                "file_size": 2000000,
                "categories": ["cs.CL"]
            }
        }
        
        mcp_client.papers_index = test_papers
        
        # Create metadata files
        for paper_id, data in test_papers.items():
            metadata_file = mcp_client._get_metadata_file_path(paper_id)
            with open(metadata_file, 'w') as f:
                json.dump({"id": paper_id, "title": data["title"]}, f)
        
        args = {}
        result = await arxiv_list_papers(args)
        
        assert result["success"] is True
        assert len(result["papers"]) == 2
        assert result["total_downloaded"] == 2
        
        # Check paper structure
        paper = result["papers"][0]
        assert "id" in paper
        assert "title" in paper
        assert "download_date" in paper
        assert "file_size" in paper
        assert "categories" in paper
        assert "local_path" in paper
        assert "metadata_available" in paper


@pytest.mark.unit
@pytest.mark.asyncio
async def test_arxiv_list_papers_with_filters(mcp_client):
    """Test listing papers with category filter."""
    with patch('src.tools.arxiv_client_mcp.mcp_client', mcp_client):
        test_papers = {
            "ai_paper": {
                "title": "AI Paper",
                "download_date": "2024-01-01T00:00:00",
                "file_size": 1000000,
                "categories": ["cs.AI"]
            },
            "ml_paper": {
                "title": "ML Paper", 
                "download_date": "2024-01-02T00:00:00",
                "file_size": 2000000,
                "categories": ["cs.LG"]
            }
        }
        
        mcp_client.papers_index = test_papers
        
        args = {"category_filter": "cs.AI"}
        result = await arxiv_list_papers(args)
        
        assert result["success"] is True
        assert len(result["papers"]) == 1
        assert result["papers"][0]["id"] == "ai_paper"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_arxiv_read_paper(mcp_client):
    """Test reading a downloaded paper."""
    with patch('src.tools.arxiv_client_mcp.mcp_client', mcp_client):
        paper_id = "test.paper"
        
        # Create fake paper file and metadata
        paper_file = mcp_client._get_paper_file_path(paper_id)
        paper_file.write_text("fake pdf content")
        
        metadata_file = mcp_client._get_metadata_file_path(paper_id)
        metadata = {
            "id": paper_id,
            "title": "Test Paper",
            "authors": [{"name": "Test Author"}]
        }
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f)
        
        args = {
            "paper_id": paper_id,
            "include_metadata": True
        }
        
        result = await arxiv_read_paper(args)
        
        assert result["success"] is True
        assert result["paper_id"] == paper_id
        assert "local_path" in result
        assert "file_size" in result
        assert "metadata" in result
        assert result["metadata"]["title"] == "Test Paper"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_arxiv_read_paper_not_found(mcp_client):
    """Test reading non-existent paper."""
    with patch('src.tools.arxiv_client_mcp.mcp_client', mcp_client):
        args = {"paper_id": "nonexistent.paper"}
        
        result = await arxiv_read_paper(args)
        
        assert result["success"] is False
        assert "not found locally" in result["error"]




@pytest.mark.unit
@pytest.mark.asyncio
async def test_arxiv_get_paper_metadata_local_cache(mcp_client):
    """Test getting metadata from local cache."""
    with patch('src.tools.arxiv_client_mcp.mcp_client', mcp_client):
        paper_id = "test.paper"
        
        # Create cached metadata
        metadata_file = mcp_client._get_metadata_file_path(paper_id)
        cached_metadata = {
            "id": paper_id,
            "title": "Cached Paper",
            "authors": [{"name": "Cached Author"}]
        }
        with open(metadata_file, 'w') as f:
            json.dump(cached_metadata, f)
        
        args = {
            "paper_id": paper_id,
            "force_refresh": False
        }
        
        result = await arxiv_get_paper_metadata(args)
        
        assert result["success"] is True
        assert result["metadata"]["title"] == "Cached Paper"
        assert "local_storage" in result["metadata"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_arxiv_get_paper_metadata_with_citations(mcp_client):
    """Test getting metadata with citation analysis."""
    with patch('src.tools.arxiv_client_mcp.mcp_client', mcp_client):
        paper_id = "test.paper"
        
        # Create metadata with abstract containing citations
        metadata_file = mcp_client._get_metadata_file_path(paper_id)
        cached_metadata = {
            "id": paper_id,
            "title": "Test Paper",
            "abstract": "This builds on work by Smith et al. (2020) and Jones et al. (2021)."
        }
        with open(metadata_file, 'w') as f:
            json.dump(cached_metadata, f)
        
        # Mock the extract_citations import
        async def mock_extract_citations(args):
            return {
                "success": True,
                "citations": [{"author": "Smith", "year": "2020"}],
                "count": 1
            }
        
        with patch('src.tools.arxiv_client_mcp.extract_citations', mock_extract_citations):
            args = {
                "paper_id": paper_id,
                "include_citations": True
            }
            
            result = await arxiv_get_paper_metadata(args)
            
            assert result["success"] is True
            assert "citations_in_abstract" in result["metadata"]
            assert "citation_count" in result["metadata"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling in various scenarios."""
    # Test missing paper ID
    result = await arxiv_download_paper({"paper_id": ""})
    assert result["success"] is False
    assert "Paper ID is required" in result["error"]
    
    result = await arxiv_read_paper({"paper_id": ""})
    assert result["success"] is False
    assert "Paper ID is required" in result["error"]
    
    result = await arxiv_get_paper_metadata({"paper_id": ""})
    assert result["success"] is False
    assert "Paper ID is required" in result["error"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_storage_path_management(temp_storage):
    """Test storage path creation and management."""
    # Test with non-existent path
    storage_path = Path(temp_storage) / "new_folder"
    client = ArxivMCPClient(storage_path=str(storage_path))
    
    assert client.storage_path.exists()
    assert client.papers_index_file.exists()


@pytest.mark.unit
def test_file_path_helpers(mcp_client):
    """Test file path helper methods."""
    paper_id = "1706.03762"
    
    paper_path = mcp_client._get_paper_file_path(paper_id)
    metadata_path = mcp_client._get_metadata_file_path(paper_id)
    
    assert paper_path.name == "1706.03762.pdf"
    assert metadata_path.name == "1706.03762_metadata.json"
    assert paper_path.parent == mcp_client.storage_path
    assert metadata_path.parent == mcp_client.storage_path