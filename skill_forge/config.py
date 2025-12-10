"""Configuration management for skill-forge."""
import os
from typing import Optional


def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from environment variable.
    
    Returns:
        API key string or None if not set.
    """
    return os.getenv("ANTHROPIC_API_KEY")


def require_api_key() -> str:
    """Require Anthropic API key, raise error if not set.
    
    Returns:
        API key string.
        
    Raises:
        ValueError: If API key is not set.
    """
    api_key = get_anthropic_api_key()
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable is required. "
            "Set it with: export ANTHROPIC_API_KEY='your-key-here'"
        )
    return api_key

