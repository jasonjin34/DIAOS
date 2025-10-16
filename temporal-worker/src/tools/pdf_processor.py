"""
PDF processing tools for academic paper content extraction.
Extracts text, sections, and metadata from research papers.
"""

import io
import re
from typing import Any, Dict, List 

import pdfplumber
import requests


async def process_pdf_content(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract and process text content from PDF.
    
    Args:
        args: Dictionary containing:
            - pdf_url: URL to PDF file
            - sections: Optional list of sections to extract
            - include_metadata: Include PDF metadata
            
    Returns:
        Processed text content with section breakdown
    """
    
    pdf_url = args.get("pdf_url", "")
    target_sections = args.get("sections", [])
    include_metadata = args.get("include_metadata", True)
    
    if not pdf_url:
        return {
            "success": False,
            "error": "PDF URL is required",
            "content": {}
        }
    
    try:
        # Download PDF
        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()
        
        pdf_content = io.BytesIO(response.content)
        
        # Extract text using pdfplumber
        extracted_content = {
            "full_text": "",
            "sections": {},
            "pages": [],
            "metadata": {}
        }
        
        with pdfplumber.open(pdf_content) as pdf:
            # Extract metadata if requested
            if include_metadata and pdf.metadata:
                extracted_content["metadata"] = {
                    "title": pdf.metadata.get("Title", ""),
                    "author": pdf.metadata.get("Author", ""),
                    "subject": pdf.metadata.get("Subject", ""),
                    "creator": pdf.metadata.get("Creator", ""),
                    "pages": len(pdf.pages)
                }
            
            # Extract text from each page
            full_text = ""
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
                    extracted_content["pages"].append({
                        "page_number": page_num + 1,
                        "text": page_text,
                        "char_count": len(page_text)
                    })
            
            extracted_content["full_text"] = full_text
            
            # Extract specific sections if requested
            if target_sections:
                sections = _extract_paper_sections(full_text, target_sections)
                extracted_content["sections"] = sections
            else:
                # Extract common academic sections
                common_sections = ["abstract", "introduction", "methodology", "results", "conclusion", "references"]
                sections = _extract_paper_sections(full_text, common_sections)
                extracted_content["sections"] = sections
        
        return {
            "success": True,
            "content": extracted_content,
            "processing_metadata": {
                "pdf_url": pdf_url,
                "file_size": len(response.content),
                "pages_processed": len(extracted_content["pages"]),
                "sections_found": len(extracted_content["sections"])
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"PDF processing failed: {str(e)}",
            "content": {},
            "pdf_url": pdf_url
        }


async def extract_paper_sections(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract specific sections from academic paper text.
    
    Args:
        args: Dictionary containing:
            - paper_text: Full paper text
            - sections: List of section names to extract
            - strict_matching: Use strict section header matching
            
    Returns:
        Dictionary mapping section names to content
    """
    
    paper_text = args.get("paper_text", "")
    target_sections = args.get("sections", [])
    strict_matching = args.get("strict_matching", False)
    
    if not paper_text:
        return {
            "success": False,
            "error": "Paper text is required",
            "sections": {}
        }
    
    try:
        sections = _extract_paper_sections(paper_text, target_sections, strict_matching)
        
        return {
            "success": True,
            "sections": sections,
            "extraction_metadata": {
                "text_length": len(paper_text),
                "sections_requested": len(target_sections),
                "sections_found": len(sections),
                "strict_matching": strict_matching
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Section extraction failed: {str(e)}",
            "sections": {}
        }


def _extract_paper_sections(
    text: str, 
    target_sections: List[str], 
    strict_matching: bool = False
) -> Dict[str, str]:
    """
    Extract sections from academic paper text using pattern matching.
    
    Args:
        text: Full paper text
        target_sections: List of section names to find
        strict_matching: Use strict header matching
        
    Returns:
        Dictionary mapping section names to extracted content
    """
    
    sections = {}
    
    # Common section header patterns
    if strict_matching:
        # Strict matching - exact section names
        section_patterns = {
            section.lower(): rf"^{re.escape(section)}\s*$"
            for section in target_sections
        }
    else:
        # Flexible matching - partial matches and variations
        section_patterns = {}
        for section in target_sections:
            section_lower = section.lower()
            if section_lower == "abstract":
                section_patterns["abstract"] = r"(?:^|\n)\s*(?:abstract|summary)\s*(?:\n|$)"
            elif section_lower == "introduction":
                section_patterns["introduction"] = r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:introduction|background)\s*(?:\n|$)"
            elif section_lower in ["methodology", "methods"]:
                section_patterns["methodology"] = r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:methodology|methods|approach)\s*(?:\n|$)"
            elif section_lower == "results":
                section_patterns["results"] = r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:results|findings|experiments)\s*(?:\n|$)"
            elif section_lower == "conclusion":
                section_patterns["conclusion"] = r"(?:^|\n)\s*(?:\d+\.?\s*)?(?:conclusion|conclusions|discussion)\s*(?:\n|$)"
            elif section_lower == "references":
                section_patterns["references"] = r"(?:^|\n)\s*(?:references|bibliography|works?\s+cited)\s*(?:\n|$)"
            else:
                # Generic pattern for other sections
                section_patterns[section_lower] = rf"(?:^|\n)\s*(?:\d+\.?\s*)?{re.escape(section_lower)}\s*(?:\n|$)"
    
    # Find section boundaries
    section_positions = []
    
    for section_name, pattern in section_patterns.items():
        matches = list(re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE))
        for match in matches:
            section_positions.append({
                "name": section_name,
                "start": match.end(),
                "header_start": match.start(),
                "header_text": match.group().strip()
            })
    
    # Sort sections by position
    section_positions.sort(key=lambda x: x["start"])
    
    # Extract content between sections
    for i, section in enumerate(section_positions):
        start_pos = section["start"]
        
        # Find end position (start of next section or end of text)
        if i + 1 < len(section_positions):
            end_pos = section_positions[i + 1]["header_start"]
        else:
            end_pos = len(text)
        
        # Extract section content
        section_content = text[start_pos:end_pos].strip()
        
        # Clean up content (remove excessive whitespace, etc.)
        section_content = re.sub(r'\n\s*\n\s*\n', '\n\n', section_content)
        section_content = re.sub(r'[ \t]+', ' ', section_content)
        
        if section_content:
            sections[section["name"]] = {
                "content": section_content,
                "header": section["header_text"],
                "word_count": len(section_content.split()),
                "char_count": len(section_content)
            }
    
    return sections


def _clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted text."""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common PDF extraction issues
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)  # Fix hyphenated words
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Normalize paragraph breaks
    
    # Remove page numbers and headers/footers (basic patterns)
    text = re.sub(r'\n\s*\d+\s*\n', '\n', text)  # Page numbers
    text = re.sub(r'\n\s*Page\s+\d+.*?\n', '\n', text, flags=re.IGNORECASE)
    
    return text.strip()