"""
Configuration settings for arXiv MCP client and local storage.
"""

import os
from pathlib import Path
from typing import Optional


class ArxivConfig:
    """Configuration class for arXiv client settings."""
    
    @classmethod
    def get_storage_path(cls) -> str:
        """Get the arXiv papers storage path from environment or default."""
        default_path = "./arxiv_papers"
        storage_path = os.getenv("ARXIV_STORAGE_PATH", default_path)
        
        # Convert to absolute path
        path = Path(storage_path).resolve()
        
        # Ensure directory exists
        path.mkdir(parents=True, exist_ok=True)
        
        return str(path)
    
    @classmethod
    def get_cache_ttl(cls) -> int:
        """Get cache TTL in seconds (default: 1 hour)."""
        return int(os.getenv("ARXIV_CACHE_TTL", "3600"))
    
    @classmethod
    def get_max_file_size(cls) -> int:
        """Get maximum file size for downloads in bytes (default: 50MB)."""
        return int(os.getenv("ARXIV_MAX_FILE_SIZE", str(50 * 1024 * 1024)))
    
    @classmethod
    def get_download_timeout(cls) -> int:
        """Get download timeout in seconds (default: 300s = 5 minutes)."""
        return int(os.getenv("ARXIV_DOWNLOAD_TIMEOUT", "300"))
    
    @classmethod
    def should_auto_cleanup(cls) -> bool:
        """Whether to automatically cleanup old papers."""
        return os.getenv("ARXIV_AUTO_CLEANUP", "false").lower() == "true"
    
    @classmethod
    def get_cleanup_days(cls) -> int:
        """Number of days after which to cleanup papers (default: 30)."""
        return int(os.getenv("ARXIV_CLEANUP_DAYS", "30"))
    
    @classmethod
    def get_max_search_results(cls) -> int:
        """Maximum number of search results to return (default: 100)."""
        return int(os.getenv("ARXIV_MAX_SEARCH_RESULTS", "100"))
    
    @classmethod
    def is_offline_mode(cls) -> bool:
        """Whether to operate in offline mode (no API calls)."""
        return os.getenv("ARXIV_OFFLINE_MODE", "false").lower() == "true"
    
    @classmethod
    def get_rate_limit_delay(cls) -> float:
        """Rate limit delay between API calls in seconds."""
        return float(os.getenv("ARXIV_RATE_LIMIT_DELAY", "1.0"))


# Configuration constants
ARXIV_CONFIG = {
    "storage_path": ArxivConfig.get_storage_path(),
    "cache_ttl": ArxivConfig.get_cache_ttl(),
    "max_file_size": ArxivConfig.get_max_file_size(),
    "download_timeout": ArxivConfig.get_download_timeout(),
    "auto_cleanup": ArxivConfig.should_auto_cleanup(),
    "cleanup_days": ArxivConfig.get_cleanup_days(),
    "max_search_results": ArxivConfig.get_max_search_results(),
    "offline_mode": ArxivConfig.is_offline_mode(),
    "rate_limit_delay": ArxivConfig.get_rate_limit_delay()
}


def validate_config() -> dict:
    """Validate configuration settings and return status."""
    issues = []
    
    # Check storage path
    storage_path = Path(ARXIV_CONFIG["storage_path"])
    if not storage_path.exists():
        try:
            storage_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            issues.append(f"Cannot create storage path: {e}")
    
    if not storage_path.is_dir():
        issues.append(f"Storage path is not a directory: {storage_path}")
    
    # Check writable
    try:
        test_file = storage_path / ".test_write"
        test_file.write_text("test")
        test_file.unlink()
    except Exception as e:
        issues.append(f"Storage path is not writable: {e}")
    
    # Validate numeric settings
    if ARXIV_CONFIG["cache_ttl"] < 0:
        issues.append("Cache TTL must be positive")
    
    if ARXIV_CONFIG["max_file_size"] < 1024:
        issues.append("Max file size too small (minimum 1KB)")
    
    if ARXIV_CONFIG["download_timeout"] < 10:
        issues.append("Download timeout too small (minimum 10s)")
    
    if ARXIV_CONFIG["cleanup_days"] < 1:
        issues.append("Cleanup days must be at least 1")
    
    if ARXIV_CONFIG["max_search_results"] < 1 or ARXIV_CONFIG["max_search_results"] > 1000:
        issues.append("Max search results must be between 1 and 1000")
    
    if ARXIV_CONFIG["rate_limit_delay"] < 0:
        issues.append("Rate limit delay must be non-negative")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "config": ARXIV_CONFIG
    }