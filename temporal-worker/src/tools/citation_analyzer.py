"""
Citation analysis tools for academic paper relationship mapping.
Extracts and analyzes citation networks from research papers.
"""

import re
from typing import Any, Dict, List, Tuple


async def extract_citations(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract citations from paper text or PDF.
    
    Args:
        args: Dictionary containing:
            - paper_text: Full text of the paper
            - paper_url: Alternative URL to paper PDF
            - format: Citation format to expect (default: mixed)
            
    Returns:
        List of extracted citations with metadata
    """
    
    paper_text = args.get("paper_text", "")
    paper_url = args.get("paper_url", "")
    citation_format = args.get("format", "mixed")
    
    if not paper_text and not paper_url:
        return {
            "success": False,
            "error": "Either paper_text or paper_url is required",
            "citations": []
        }
    
    try:
        # If URL provided, fetch content (simplified for demo)
        if paper_url and not paper_text:
            # In real implementation, would use PDF extraction
            paper_text = f"Content from {paper_url} would be extracted here"
        
        # Extract citations using multiple patterns
        citations = []
        
        # Pattern 1: Author (Year) format
        author_year_pattern = r'([A-Z][a-z]+(?:\s+et\s+al\.?)?)\s*\((\d{4})\)'
        author_year_matches = re.findall(author_year_pattern, paper_text)
        
        for author, year in author_year_matches:
            citations.append({
                "type": "author_year",
                "author": author,
                "year": year,
                "format": "apa_style"
            })
        
        # Pattern 2: [Number] format
        numbered_pattern = r'\[(\d+)\]'
        numbered_matches = re.findall(numbered_pattern, paper_text)
        
        for num in numbered_matches:
            citations.append({
                "type": "numbered",
                "reference_number": num,
                "format": "ieee_style"
            })
        
        # Pattern 3: DOI extraction
        doi_pattern = r'doi:?\s*(10\.\d+/[^\s]+)'
        doi_matches = re.findall(doi_pattern, paper_text, re.IGNORECASE)
        
        for doi in doi_matches:
            citations.append({
                "type": "doi",
                "doi": doi,
                "format": "doi_reference"
            })
        
        # Pattern 4: arXiv ID extraction
        arxiv_pattern = r'arXiv:(\d{4}\.\d{4,5})'
        arxiv_matches = re.findall(arxiv_pattern, paper_text)
        
        for arxiv_id in arxiv_matches:
            citations.append({
                "type": "arxiv",
                "arxiv_id": arxiv_id,
                "format": "arxiv_reference"
            })
        
        # Remove duplicates
        unique_citations = []
        seen = set()
        
        for citation in citations:
            citation_key = f"{citation['type']}_{citation.get('author', '')}{citation.get('year', '')}{citation.get('doi', '')}{citation.get('arxiv_id', '')}"
            if citation_key not in seen:
                seen.add(citation_key)
                unique_citations.append(citation)
        
        return {
            "success": True,
            "citations": unique_citations,
            "count": len(unique_citations),
            "extraction_metadata": {
                "text_length": len(paper_text),
                "patterns_used": ["author_year", "numbered", "doi", "arxiv"],
                "format": citation_format
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Citation extraction failed: {str(e)}",
            "citations": []
        }


async def analyze_citation_network(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze citation relationships between papers.
    
    Args:
        args: Dictionary containing:
            - paper_ids: List of paper IDs to analyze
            - depth: Citation depth to explore (default: 2)
            - include_co_citations: Include co-citation analysis
            
    Returns:
        Citation network analysis with relationships and metrics
    """
    
    paper_ids = args.get("paper_ids", [])
    depth = args.get("depth", 2)
    include_co_citations = args.get("include_co_citations", True)
    
    if not paper_ids:
        return {
            "success": False,
            "error": "At least one paper ID is required",
            "network": {}
        }
    
    try:
        # Build citation network
        network = {
            "nodes": [],
            "edges": [],
            "metrics": {}
        }
        
        # Process each paper
        for paper_id in paper_ids:
            # Add paper as node
            node = {
                "id": paper_id,
                "type": "paper",
                "properties": {
                    "paper_id": paper_id,
                    "title": f"Paper {paper_id}",  # Would fetch real title
                    "citation_count": 0,
                    "reference_count": 0
                }
            }
            network["nodes"].append(node)
            
            # Simulate citation analysis (in real implementation, would query citation databases)
            cited_papers = _simulate_cited_papers(paper_id, depth)
            citing_papers = _simulate_citing_papers(paper_id, depth)
            
            # Add cited papers as nodes and edges
            for cited_id, relationship in cited_papers:
                if not any(n["id"] == cited_id for n in network["nodes"]):
                    network["nodes"].append({
                        "id": cited_id,
                        "type": "cited_paper",
                        "properties": {
                            "paper_id": cited_id,
                            "title": f"Cited Paper {cited_id}",
                            "relationship_type": relationship
                        }
                    })
                
                network["edges"].append({
                    "source": paper_id,
                    "target": cited_id,
                    "type": "cites",
                    "properties": {
                        "relationship": relationship,
                        "depth": 1
                    }
                })
            
            # Add citing papers
            for citing_id, relationship in citing_papers:
                if not any(n["id"] == citing_id for n in network["nodes"]):
                    network["nodes"].append({
                        "id": citing_id,
                        "type": "citing_paper",
                        "properties": {
                            "paper_id": citing_id,
                            "title": f"Citing Paper {citing_id}",
                            "relationship_type": relationship
                        }
                    })
                
                network["edges"].append({
                    "source": citing_id,
                    "target": paper_id,
                    "type": "cites",
                    "properties": {
                        "relationship": relationship,
                        "depth": 1
                    }
                })
        
        # Calculate network metrics
        network["metrics"] = {
            "total_nodes": len(network["nodes"]),
            "total_edges": len(network["edges"]),
            "average_citations": len(network["edges"]) / len(paper_ids) if paper_ids else 0,
            "network_density": _calculate_network_density(network),
            "central_papers": _find_central_papers(network)
        }
        
        # Co-citation analysis if requested
        if include_co_citations:
            co_citations = _analyze_co_citations(network)
            network["co_citations"] = co_citations
        
        return {
            "success": True,
            "network": network,
            "analysis_metadata": {
                "papers_analyzed": len(paper_ids),
                "depth": depth,
                "include_co_citations": include_co_citations
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Citation network analysis failed: {str(e)}",
            "network": {}
        }


def _simulate_cited_papers(paper_id: str, depth: int) -> List[Tuple[str, str]]:
    """Simulate cited papers (would use real citation database in production)."""
    base_num = hash(paper_id) % 100
    return [
        (f"cited_{base_num + i}", "direct_citation")
        for i in range(min(5, depth * 2))
    ]


def _simulate_citing_papers(paper_id: str, depth: int) -> List[Tuple[str, str]]:
    """Simulate citing papers (would use real citation database in production)."""
    base_num = hash(paper_id) % 100
    return [
        (f"citing_{base_num + i}", "direct_citation")
        for i in range(min(3, depth))
    ]


def _calculate_network_density(network: Dict[str, Any]) -> float:
    """Calculate network density (actual edges / possible edges)."""
    nodes = len(network["nodes"])
    edges = len(network["edges"])
    
    if nodes < 2:
        return 0.0
    
    possible_edges = nodes * (nodes - 1)
    return edges / possible_edges if possible_edges > 0 else 0.0


def _find_central_papers(network: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find papers with highest citation centrality."""
    paper_citations = {}
    
    for edge in network["edges"]:
        target = edge["target"]
        if target in paper_citations:
            paper_citations[target] += 1
        else:
            paper_citations[target] = 1
    
    # Sort by citation count
    sorted_papers = sorted(
        paper_citations.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [
        {
            "paper_id": paper_id,
            "citation_count": count,
            "centrality_rank": idx + 1
        }
        for idx, (paper_id, count) in enumerate(sorted_papers[:5])
    ]


def _analyze_co_citations(network: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze co-citation patterns in the network."""
    co_citations = {}
    
    # Find papers that cite the same papers
    citing_relationships = {}
    
    for edge in network["edges"]:
        source = edge["source"]
        target = edge["target"]
        
        if target not in citing_relationships:
            citing_relationships[target] = []
        citing_relationships[target].append(source)
    
    # Find co-citation pairs
    for cited_paper, citing_papers in citing_relationships.items():
        if len(citing_papers) > 1:
            for i, paper1 in enumerate(citing_papers):
                for paper2 in citing_papers[i+1:]:
                    pair = tuple(sorted([paper1, paper2]))
                    if pair not in co_citations:
                        co_citations[pair] = []
                    co_citations[pair].append(cited_paper)
    
    return {
        "co_citation_pairs": len(co_citations),
        "strongest_co_citations": [
            {
                "papers": list(pair),
                "shared_citations": len(shared),
                "shared_papers": shared
            }
            for pair, shared in sorted(
                co_citations.items(),
                key=lambda x: len(x[1]),
                reverse=True
            )[:5]
        ]
    }